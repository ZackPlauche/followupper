"""
Campaign message scheduler using APScheduler.
"""
import logging
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pytz
from django.utils import timezone
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from .models import CampaignAssignment, Campaign, PlatformCredentials, Contact, AutomationSettings

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

        # Schedule job to run at the configured interval
        self.scheduler.add_job(
            self.process_due_messages,
            trigger=IntervalTrigger(minutes=check_interval),
            id='process_due_messages',
            name='Process due campaign messages',
            replace_existing=True
        )
        logger.info(f"Scheduled periodic job to process due messages (runs every {check_interval} minute(s))")

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

        # Process scheduled messages from message_chains
        self.process_scheduled_message_chains(now)

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
        platform_pref = contact.platform_preference or 'email'
        if platform_pref == 'email' and contact.email:
            recipient = contact.email
            platform = 'email'
        elif platform_pref == 'codementor' and contact.codementor_username:
            recipient = contact.codementor_username
            platform = 'codementor'
        elif contact.email:
            recipient = contact.email
            platform = 'email'
        else:
            logger.warning(f"Contact {contact.id} has no valid contact method, skipping")
            return

        # Send the message
        try:
            if platform == 'email':
                self._send_email(contact, message_body)
            elif platform == 'codementor':
                # TODO: Implement Codementor sending
                logger.warning(f"Codementor sending not yet implemented for contact {contact.id}")
                return
            else:
                logger.warning(f"Unknown platform {platform} for contact {contact.id}")
                return

            # Calculate next send date
            next_send_date = self._calculate_next_send_date(campaign, assignment)

            # Update assignment
            assignment.next_send_date = next_send_date
            assignment.save(update_fields=['next_send_date'])

            logger.info(f"Successfully sent message to {contact.name} ({recipient}), next send: {next_send_date}")

        except Exception as e:
            logger.error(f"Failed to send message to {contact.name}: {str(e)}", exc_info=True)
            # Don't update next_send_date on failure - will retry on next check
            raise

    def _send_email(self, contact, body, subject=None):
        """Send an email using Gmail client."""
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

        client.send_email(to=contact.email, subject=subject, body=body)

    def _replace_template_variables(self, template, data):
        """Replace template variables in message."""
        message = template
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

    def process_scheduled_message_chains(self, now):
        """Process scheduled messages from Contact.message_chains."""
        import json

        # Get all active contacts with message_chains
        contacts = Contact.objects.filter(
            is_active=True
        ).exclude(message_chains='').exclude(message_chains__isnull=True)

        logger.info(f"Checking {contacts.count()} contacts for scheduled messages in message_chains")
        processed_count = 0
        for contact in contacts:
            try:
                if not contact.message_chains:
                    continue

                # Parse message_chains JSON
                try:
                    chains = json.loads(contact.message_chains)
                except (json.JSONDecodeError, TypeError):
                    logger.warning(f"Invalid message_chains JSON for contact {contact.id}, skipping")
                    continue

                if not isinstance(chains, list):
                    continue

                # Process each chain
                updated_chains = []
                has_changes = False

                for chain_index, chain in enumerate(chains):
                    if not isinstance(chain, list):
                        updated_chains.append(chain)
                        continue

                    updated_chain = []

                    # Check if this is an interval-based chain (has chain_start_date in first message)
                    first_msg = chain[0] if chain and isinstance(chain[0], dict) else None
                    is_interval_chain = first_msg and first_msg.get('chain_start_date') and first_msg.get('chain_start_time')

                    if is_interval_chain:
                        # Process interval-based chain
                        chain_start_date = first_msg.get('chain_start_date')
                        chain_start_time = first_msg.get('chain_start_time', '09:00')
                        chain_timezone_str = first_msg.get('chain_timezone', 'UTC')

                        # Parse chain start timezone
                        try:
                            chain_tz = pytz.timezone(chain_timezone_str)
                        except pytz.exceptions.UnknownTimeZoneError:
                            logger.warning(f"Unknown chain timezone '{chain_timezone_str}' for contact {contact.id}, using UTC")
                            chain_tz = pytz.UTC

                        # Parse chain start datetime
                        try:
                            start_datetime_str = f"{chain_start_date}T{chain_start_time}"
                            naive_start_dt = datetime.strptime(start_datetime_str, "%Y-%m-%dT%H:%M")
                            chain_start_dt = chain_tz.localize(naive_start_dt).astimezone(pytz.UTC)
                        except (ValueError, KeyError) as e:
                            logger.warning(f"Error parsing chain start date/time for contact {contact.id}: {str(e)}")
                            # Keep all messages if we can't parse start time
                            updated_chains.append(chain)
                            continue

                        # Process each message in the interval chain
                        cumulative_days = 0
                        for msg_index, msg in enumerate(chain):
                            if not isinstance(msg, dict):
                                updated_chain.append(msg)
                                continue

                            # Get frequency_days for this message
                            frequency_days = msg.get('frequency_days', 0)

                            # Skip if already sent (but still add to cumulative for remaining messages)
                            if msg.get('sent', False):
                                cumulative_days += frequency_days
                                # Keep sent messages in chain for cumulative calculation
                                updated_chain.append(msg)
                                continue

                            # Calculate when this message should be sent
                            # Send time: chain_start + cumulative_days + this message's frequency_days
                            message_send_dt = chain_start_dt + timedelta(days=cumulative_days + frequency_days)

                            # Check if due
                            if message_send_dt <= now:
                                # Send the message
                                try:
                                    self.send_scheduled_message(contact, msg)
                                    processed_count += 1
                                    has_changes = True
                                    # Mark as sent and keep in chain for cumulative calculation
                                    msg['sent'] = True
                                    updated_chain.append(msg)
                                    logger.info(f"Sent interval message {msg_index + 1} to {contact.name} (contact {contact.id})")
                                except Exception as e:
                                    logger.error(f"Failed to send interval message to {contact.name}: {str(e)}", exc_info=True)
                                    # Keep the message if sending failed
                                    updated_chain.append(msg)
                            else:
                                # Not due yet, keep it
                                updated_chain.append(msg)

                            # Update cumulative for next message (add this message's frequency_days)
                            cumulative_days += frequency_days

                    else:
                        # Process scheduled messages (specific date/time mode)
                        for msg_index, msg in enumerate(chain):
                            if not isinstance(msg, dict):
                                updated_chain.append(msg)
                                continue

                            # Check if this message is scheduled and due
                            if msg.get('schedule') and msg.get('send_date') and msg.get('send_time'):
                                try:
                                    # Parse send date and time
                                    send_date_str = msg.get('send_date')
                                    send_time_str = msg.get('send_time')

                                    # Combine date and time
                                    datetime_str = f"{send_date_str}T{send_time_str}"

                                    # Parse in message's timezone (if specified) or contact's timezone
                                    message_tz_str = msg.get('timezone')
                                    if message_tz_str:
                                        # Use timezone from message
                                        try:
                                            tz = pytz.timezone(message_tz_str)
                                        except pytz.exceptions.UnknownTimeZoneError:
                                            logger.warning(f"Unknown timezone '{message_tz_str}' in message for contact {contact.id}, using contact timezone")
                                            try:
                                                tz = pytz.timezone(contact.timezone) if contact.timezone else pytz.UTC
                                            except pytz.exceptions.UnknownTimeZoneError:
                                                tz = pytz.UTC
                                    else:
                                        # Fall back to contact's timezone
                                        try:
                                            tz = pytz.timezone(contact.timezone) if contact.timezone else pytz.UTC
                                        except pytz.exceptions.UnknownTimeZoneError:
                                            logger.warning(f"Unknown timezone '{contact.timezone}' for contact {contact.id}, using UTC")
                                            tz = pytz.UTC

                                    naive_dt = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M")

                                    # Localize to the determined timezone, then convert to UTC
                                    local_dt = tz.localize(naive_dt)
                                    utc_dt = local_dt.astimezone(pytz.UTC)

                                    # Check if due (with 1 minute tolerance)
                                    if utc_dt <= now:
                                        # Send the message
                                        try:
                                            self.send_scheduled_message(contact, msg)
                                            processed_count += 1
                                            has_changes = True
                                            # Don't add this message to updated_chain (it's been sent)
                                            logger.info(f"Sent scheduled message to {contact.name} (contact {contact.id})")
                                        except Exception as e:
                                            logger.error(f"Failed to send scheduled message to {contact.name}: {str(e)}", exc_info=True)
                                            # Keep the message in the chain if sending failed
                                            updated_chain.append(msg)
                                    else:
                                        # Not due yet, keep it
                                        updated_chain.append(msg)
                                except (ValueError, KeyError) as e:
                                    logger.warning(f"Error parsing scheduled message date/time for contact {contact.id}: {str(e)}")
                                    # Keep the message if we can't parse it
                                    updated_chain.append(msg)
                            else:
                                # Not a scheduled message, keep it
                                updated_chain.append(msg)

                    # Only keep non-empty chains
                    if updated_chain:
                        updated_chains.append(updated_chain)
                    else:
                        has_changes = True

                # Update contact if chains changed
                if has_changes:
                    if updated_chains:
                        contact.message_chains = json.dumps(updated_chains)
                    else:
                        contact.message_chains = ''
                    contact.save(update_fields=['message_chains'])

            except Exception as e:
                logger.error(f"Error processing message_chains for contact {contact.id}: {str(e)}", exc_info=True)

        if processed_count > 0:
            logger.info(f"Processed {processed_count} scheduled messages from message_chains")

    def send_scheduled_message(self, contact, message):
        """Send a scheduled message from message_chains."""
        subject = message.get('subject', '')
        body = message.get('body', '')

        if not body:
            raise Exception("Message body is empty")

        # Determine platform and recipient
        platform_pref = contact.platform_preference or 'email'
        if platform_pref == 'email' and contact.email:
            recipient = contact.email
            platform = 'email'
        elif platform_pref == 'codementor' and contact.codementor_username:
            recipient = contact.codementor_username
            platform = 'codementor'
        elif contact.email:
            recipient = contact.email
            platform = 'email'
        else:
            raise Exception(f"Contact {contact.id} has no valid contact method")

        # Send the message
        if platform == 'email':
            # Use subject from message, or generate default
            msg_subject = subject if subject else f"Follow-up: {contact.name}"
            self._send_email(contact, body, subject=msg_subject)
        elif platform == 'codementor':
            # TODO: Implement Codementor sending
            logger.warning(f"Codementor sending not yet implemented for contact {contact.id}")
            raise Exception("Codementor sending not yet implemented")
        else:
            raise Exception(f"Unknown platform {platform}")


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
