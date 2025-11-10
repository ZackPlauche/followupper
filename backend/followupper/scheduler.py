"""
Campaign message scheduler using APScheduler.
"""
import logging
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pytz
from django.utils import timezone
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from .models import CampaignAssignment, Campaign, PlatformCredentials, Contact, AutomationSettings, MessageSequence, Message

logger = logging.getLogger('followupper')


class CampaignScheduler:
    """Manages scheduled sending of campaign messages."""

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        logger.info("Campaign scheduler started")

    def start(self):
        """Start the scheduler and add periodic job."""
        if not self.scheduler.running:
            self.scheduler.start()

        # Get automation settings
        automation_settings = AutomationSettings.get_settings()

        # Only schedule if enabled
        if not automation_settings.enabled:
            logger.info("Scheduler is disabled in automation settings")
            return

        # Get check interval (enforce minimum of 1 minute for accuracy)
        check_interval = automation_settings.get_check_interval()

        # Schedule job to run at the start of each minute
        # If interval is 1 minute, run every minute at :00
        # If interval is > 1 minute, run at :00, :01*interval, :02*interval, etc.
        if check_interval == 1:
            trigger = CronTrigger(minute='*')  # Every minute at :00
        else:
            # Run at :00, :interval, :2*interval, etc. each hour
            trigger = CronTrigger(minute=f'*/{check_interval}')

        self.scheduler.add_job(
            self.process_due_messages,
            trigger=trigger,
            id='process_due_messages',
            name='Process due campaign messages',
            replace_existing=True
        )
        logger.info(f"Scheduled periodic job to process due messages (runs every {check_interval} minute(s) at the start of each minute)")

    def stop(self):
        """Stop the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Campaign scheduler stopped")

    def process_due_messages(self):
        """Process all campaign assignments and scheduled messages that are due to be sent."""
        # Check if automation is enabled
        automation_settings = AutomationSettings.get_settings()
        if not automation_settings.enabled:
            logger.debug("Skipping message processing - automation is disabled")
            return

        now = timezone.now()

        # Find all active assignments that are due
        due_assignments = CampaignAssignment.objects.filter(
            status='active',
            next_send_date__lte=now,
            campaign__is_active=True,
            campaign__campaign_type='recurring'
        ).select_related('campaign', 'contact')

        logger.info(f"Found {due_assignments.count()} due assignments to process")

        for assignment in due_assignments:
            try:
                self.send_campaign_message(assignment)
            except Exception as e:
                logger.error(f"Error processing assignment {assignment.id}: {str(e)}", exc_info=True)

        # Process scheduled messages from Message model
        self.process_scheduled_messages(now)

    def send_campaign_message(self, assignment):
        """Send a message for a campaign assignment and schedule the next one."""
        campaign = assignment.campaign
        contact = assignment.contact

        # Get message content
        message_template = campaign.next_message_override or campaign.message_template or ''
        if not message_template:
            logger.warning(f"Campaign {campaign.id} has no message template, skipping")
            return

        # Replace template variables
        template_data = contact.get_template_data()
        message_body = self._replace_template_variables(message_template, template_data)

        # Determine platform and recipient
        # Handle both legacy string format and new array format
        import json
        platform_pref = contact.platform_preference or 'email'
        platforms = []
        try:
            # Try to parse as JSON array (new format)
            parsed = json.loads(platform_pref)
            if isinstance(parsed, list):
                platforms = parsed
            else:
                # Legacy format
                if platform_pref == 'both':
                    platforms = ['email', 'codementor']
                else:
                    platforms = [platform_pref]
        except (json.JSONDecodeError, TypeError, AttributeError):
            # Legacy format: string
            if platform_pref == 'both':
                platforms = ['email', 'codementor']
            else:
                platforms = [platform_pref] if platform_pref else ['email']

        # Use first available platform from preference
        platform = None
        recipient = None
        for pref in platforms:
            if pref == 'email' and contact.email:
                platform = 'email'
                recipient = contact.email
                break
            elif pref == 'codementor' and contact.codementor_username:
                platform = 'codementor'
                recipient = contact.codementor_username
                break

        # Fallback to email if no preference match
        if not platform:
            if contact.email:
                platform = 'email'
                recipient = contact.email
            else:
                logger.warning(f"Contact {contact.id} has no valid contact method, skipping")
                return

        # Send the message
        try:
            if platform == 'email':
                self._send_email(contact, message_body)
            elif platform == 'codementor':
                self._send_codementor_message(contact, message_body)
            else:
                logger.warning(f"Unknown platform {platform} for contact {contact.id}")
                return

            # Calculate next send date
            next_send_date = self._calculate_next_send_date(campaign, assignment)

            # Update assignment
            assignment.next_send_date = next_send_date
            assignment.save(update_fields=['next_send_date'])

            # Update contact's last_messaged field
            contact.last_messaged = timezone.now()
            contact.save(update_fields=['last_messaged'])

            logger.info(f"Successfully sent message to {contact.name} ({recipient}), next send: {next_send_date}")

        except Exception as e:
            logger.error(f"Failed to send message to {contact.name}: {str(e)}", exc_info=True)
            # Don't update next_send_date on failure - will retry on next check
            raise

    def _send_email(self, contact, body, subject=None, reply_to_message_id=None):
        """Send an email using Gmail client.

        Args:
            contact: Contact instance
            body: Email body text
            subject: Email subject (optional)
            reply_to_message_id: Gmail message ID to reply to (optional, for threading)

        Returns:
            str: The Gmail message ID of the sent email
        """
        from gmail import Client

        # Get Gmail credentials
        gmail_creds = PlatformCredentials.objects.filter(platform='gmail').first()
        if not gmail_creds:
            raise Exception("Gmail credentials not configured")

        gmail_data = gmail_creds.get_credentials()
        gmail_email = gmail_data.get('email', '').strip()
        app_password = gmail_data.get('app_password', '').strip()
        gmail_name = gmail_data.get('name', '').strip()

        if not gmail_email or not app_password:
            raise Exception("Gmail credentials are incomplete")

        if not contact.email:
            raise Exception(f"Contact {contact.name} has no email address")

        # Create Gmail client and send
        client_kwargs = {'email': gmail_email, 'app_password': app_password}
        if gmail_name:
            client_kwargs['name'] = gmail_name

        client = Client(**client_kwargs)

        # Use provided subject or generate default
        if subject is None:
            subject = f"Follow-up: {contact.name}"

        # Send email with optional reply threading
        if reply_to_message_id:
            message_id = client.send_email(
                to=contact.email,
                subject=subject,
                body=body,
                reply_to_message_id=reply_to_message_id
            )
        else:
            message_id = client.send_email(to=contact.email, subject=subject, body=body)

        return message_id

    def _send_codementor_message(self, contact, body):
        """Send a message via Codementor API.

        Args:
            contact: Contact instance with codementor_username
            body: Message body text

        Returns:
            bool: True if message was sent successfully
        """
        import codementorapi

        # Get Codementor credentials
        codementor_creds = PlatformCredentials.objects.filter(platform='codementor').first()
        if not codementor_creds:
            raise Exception("Codementor credentials not configured")

        creds_data = codementor_creds.get_credentials()
        access_token = creds_data.get('access_token', '').strip()
        refresh_token = creds_data.get('refresh_token', '').strip()

        if not access_token or not refresh_token:
            raise Exception("Codementor credentials are incomplete")

        if not contact.codementor_username:
            raise Exception(f"Contact {contact.name} has no Codementor username")

        # Create Codementor client and send message
        client = codementorapi.Client(
            access_token=access_token,
            refresh_token=refresh_token
        )

        client.send_message(contact.codementor_username, body)
        return True

    def _replace_template_variables(self, template, data):
        """Replace template variables in message."""
        message = template

        # Extract all available fields from contact/user data
        contact_data = data.get('contact', {})
        user_data = data.get('user', {})

        # Get gender (prefer contact, fallback to user)
        gender = contact_data.get('gender', '') or user_data.get('gender', '')

        # Handle gender-based conditionals first (e.g., {if_male:text}{if_female:text})
        import re
        # Replace {if_male:text} blocks
        if gender == 'male':
            message = re.sub(r'\{if_male:([^}]+)\}', r'\1', message)
            message = re.sub(r'\{if_female:([^}]+)\}', '', message)
        elif gender == 'female':
            message = re.sub(r'\{if_female:([^}]+)\}', r'\1', message)
            message = re.sub(r'\{if_male:([^}]+)\}', '', message)
        else:
            # If gender not specified, remove both blocks
            message = re.sub(r'\{if_male:([^}]+)\}', '', message)
            message = re.sub(r'\{if_female:([^}]+)\}', '', message)

        # Create a flat mapping for simplified syntax
        simplified_vars = {}
        for key, value in contact_data.items():
            simplified_vars[key] = str(value)
        # User data takes precedence if it exists
        for key, value in user_data.items():
            simplified_vars[key] = str(value)

        # Replace simplified syntax (e.g., {first_name}, {name})
        for var_name, var_value in simplified_vars.items():
            message = message.replace(f'{{{var_name}}}', var_value)

        # Then handle old syntax for backwards compatibility (e.g., {contact.first_name}, {user.name})
        for key, value in data.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    message = message.replace(f'{{{key}.{sub_key}}}', str(sub_value))
            else:
                message = message.replace(f'{{{key}}}', str(value))

        return message

    def _calculate_next_send_date(self, campaign, assignment):
        """Calculate the next send date (reuses logic from serializer)."""
        from .serializers import CampaignAssignmentSerializer

        serializer = CampaignAssignmentSerializer()
        return serializer._calculate_next_send_date(campaign, assignment)

    def process_scheduled_messages(self, now):
        """Process scheduled messages from Message model."""
        # Get all pending messages that are due
        pending_messages = Message.objects.filter(
            status='pending'
        ).select_related('contact', 'sequence').order_by('send_date', 'send_time')

        logger.info(f"Checking {pending_messages.count()} pending messages")
        processed_count = 0

        for message in pending_messages:
            try:
                contact = message.contact
                if not contact.is_active:
                    continue

                # Determine if message is due
                is_due = False
                send_datetime = None

                if message.sequence and message.sequence.timing_type == 'interval':
                    # Interval-based message - calculate from sequence start
                    sequence = message.sequence
                    if sequence.chain_start_date and sequence.chain_start_time:
                        try:
                            # Parse chain start timezone
                            chain_tz_str = sequence.chain_timezone or 'UTC'
                            try:
                                chain_tz = pytz.timezone(chain_tz_str)
                            except pytz.exceptions.UnknownTimeZoneError:
                                chain_tz = pytz.UTC

                            # Parse chain start datetime
                            start_datetime_str = f"{sequence.chain_start_date}T{sequence.chain_start_time}"
                            naive_start_dt = datetime.strptime(start_datetime_str, "%Y-%m-%dT%H:%M")
                            chain_start_dt = chain_tz.localize(naive_start_dt).astimezone(pytz.UTC)

                            # Calculate cumulative days for this message
                            # Get all messages in sequence before this one
                            previous_messages = Message.objects.filter(
                                sequence=sequence,
                                order__lt=message.order
                            ).order_by('order')

                            cumulative_days = 0
                            for prev_msg in previous_messages:
                                cumulative_days += prev_msg.frequency_days

                            # Add this message's frequency_days
                            cumulative_days += message.frequency_days

                            # Calculate send datetime
                            send_datetime = chain_start_dt + timedelta(days=cumulative_days)
                            is_due = send_datetime <= now

                        except (ValueError, KeyError) as e:
                            logger.warning(f"Error parsing interval sequence start for message {message.id}: {str(e)}")
                            continue

                elif message.send_date and message.send_time:
                    # Specific date/time message
                    try:
                        # Handle TimeField - convert to string format
                        time_str = str(message.send_time)
                        # If it's in HH:MM:SS format, take only HH:MM
                        if ':' in time_str:
                            time_parts = time_str.split(':')
                            time_str = f"{time_parts[0]}:{time_parts[1]}"

                        datetime_str = f"{message.send_date}T{time_str}"
                        message_tz_str = message.timezone or contact.timezone or 'UTC'
                        try:
                            tz = pytz.timezone(message_tz_str)
                        except pytz.exceptions.UnknownTimeZoneError:
                            tz = pytz.UTC

                        naive_dt = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M")
                        local_dt = tz.localize(naive_dt)
                        send_datetime = local_dt.astimezone(pytz.UTC)
                        is_due = send_datetime <= now

                    except (ValueError, KeyError) as e:
                        logger.warning(f"Error parsing scheduled message date/time for message {message.id}: {str(e)}")
                        continue

                if is_due:
                    # Send the message
                    try:
                        self.send_scheduled_message(contact, message)
                        processed_count += 1
                        logger.info(f"Sent scheduled message {message.id} to {contact.name} (contact {contact.id})")
                    except Exception as e:
                        logger.error(f"Failed to send scheduled message {message.id} to {contact.name}: {str(e)}", exc_info=True)

            except Exception as e:
                logger.error(f"Error processing message {message.id}: {str(e)}", exc_info=True)

        if processed_count > 0:
            logger.info(f"Processed {processed_count} scheduled messages")

    def send_scheduled_message(self, contact, message):
        """Send a scheduled message from Message model."""
        # message can be either a Message instance or a dict (for backwards compatibility)
        if isinstance(message, Message):
            subject = message.subject or ''
            body = message.body or ''
            platforms = message.platforms or []
        else:
            # Legacy dict format (shouldn't happen but handle it)
            subject = message.get('subject', '')
            body = message.get('body', '')
            platforms = message.get('platforms', [])

        if not body:
            raise Exception("Message body is empty")

        # If no platforms specified, fallback to contact platform preference
        if not platforms or not isinstance(platforms, list):
            platforms = contact.platform_preference or []
            if not isinstance(platforms, list):
                platforms = ['email']  # Default fallback

        # For chain messages (sequences) that use email, find previous email message to thread replies
        reply_to_message_id = None
        if isinstance(message, Message) and message.sequence and 'email' in platforms:
            # Find the most recent sent email message in this sequence
            # Get all previous sent messages in order
            previous_messages = Message.objects.filter(
                sequence=message.sequence,
                status='sent',
                order__lt=message.order
            ).order_by('-order')

            # Find the first one that was sent via email and has an email_message_id
            for prev_msg in previous_messages:
                if prev_msg.platforms and 'email' in prev_msg.platforms and prev_msg.email_message_id:
                    reply_to_message_id = prev_msg.email_message_id
                    break

        # Send via all available platforms from the list
        sent_platforms = []
        email_message_id = None
        for platform in platforms:
            if platform == 'email' and contact.email:
                # Use subject from message, or generate default
                msg_subject = subject if subject else f"Follow-up: {contact.name}"
                email_message_id = self._send_email(
                    contact,
                    body,
                    subject=msg_subject,
                    reply_to_message_id=reply_to_message_id
                )
                sent_platforms.append('email')
            elif platform == 'codementor' and contact.codementor_username:
                self._send_codementor_message(contact, body)
                sent_platforms.append('codementor')
            else:
                logger.warning(f"Platform {platform} not available for contact {contact.id}, skipping")

        if not sent_platforms:
            raise Exception(f"Contact {contact.id} has no valid contact method for any of the specified platforms")

        # Update message status and store email_message_id
        try:
            sent_time = timezone.now()
            if isinstance(message, Message):
                message.status = 'sent'
                message.sent_at = sent_time
                if email_message_id:
                    message.email_message_id = email_message_id
                message.save(update_fields=['status', 'sent_at', 'email_message_id'])

                # Update contact's last_messaged field
                contact.last_messaged = sent_time
                contact.save(update_fields=['last_messaged'])

                # Create history record (Message with status='sent' serves as history)
                # The message itself is already the history, but we could create a separate one if needed
                # For now, the sent message IS the history
            else:
                # Legacy dict format - create a new Message record for history
                sent_time = timezone.now()
                Message.objects.create(
                    contact=contact,
                    subject=subject if 'email' in sent_platforms else '',
                    body=body,
                    platforms=sent_platforms,
                    status='sent',
                    sent_at=sent_time
                )
                # Update contact's last_messaged field
                contact.last_messaged = sent_time
                contact.save(update_fields=['last_messaged'])
        except Exception as e:
            # Log but don't fail the request
            logger.error(f"Failed to update message status for contact {contact.id}: {str(e)}")


# Global scheduler instance
_scheduler = None


def get_scheduler():
    """Get or create the global scheduler instance."""
    global _scheduler
    if _scheduler is None:
        _scheduler = CampaignScheduler()
    return _scheduler


def start_scheduler():
    """Start the campaign scheduler."""
    scheduler = get_scheduler()
    scheduler.start()


def stop_scheduler():
    """Stop the campaign scheduler."""
    global _scheduler
    if _scheduler is not None:
        _scheduler.stop()
        _scheduler = None


def restart_scheduler():
    """Restart the scheduler with current automation settings."""
    global _scheduler
    if _scheduler is not None:
        # Remove existing job
        try:
            _scheduler.scheduler.remove_job('process_due_messages')
        except Exception:
            pass
        # Restart with new settings
        _scheduler.start()
        logger.info("Scheduler restarted with updated settings")
    else:
        # If scheduler doesn't exist, start it
        start_scheduler()
