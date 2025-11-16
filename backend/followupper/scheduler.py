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

from .models import CampaignAssignment, Campaign, PlatformCredentials, Contact, AutomationSettings, MessageSequence, Message, UserSettings
from .rate_limiter import CodementorRateLimiter

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

        # Get message content - use assignment's custom message override if available
        message_template = assignment.custom_message_override or campaign.next_message_override or campaign.message_template or ''
        if not message_template:
            logger.warning(f"Campaign {campaign.id} has no message template, skipping")
            return

        # Replace template variables
        template_data = contact.get_template_data()
        
        # Determine frequency type and days
        # If assignment has custom_frequency_days, determine type from days
        # Otherwise use campaign's frequency_type
        if assignment.custom_frequency_days:
            frequency_days = assignment.custom_frequency_days
            frequency_type = self._days_to_frequency_type(frequency_days)
        else:
            frequency_type = campaign.frequency_type or 'weekly'
            frequency_days = campaign.default_frequency_days or 7
        
        # Set frequency to simple word (day, week, month, quarter, year)
        frequency_map = {
            'daily': 'day',
            'weekly': 'week',
            'monthly': 'month',
            'quarterly': 'quarter',
            'yearly': 'year',
            'custom': 'period'
        }
        frequency_word = frequency_map.get(frequency_type, '')
        template_data['frequency'] = frequency_word
        template_data['frequency_type'] = frequency_type
        template_data['frequency_days'] = str(frequency_days)
        
        # Add seasonal information
        season_info = self._get_current_season()
        template_data['season'] = season_info.get('season')
        template_data['holiday'] = season_info.get('holiday')
        
        message_body = self._replace_template_variables(message_template, template_data, frequency_type)

        # Get subject for recurring campaigns
        subject = None
        if campaign.campaign_type == 'recurring' and campaign.subject_template:
            subject = self._replace_template_variables(campaign.subject_template, template_data, frequency_type)

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
                self._send_email(contact, message_body, subject=subject)
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
        """Send a message via Codementor API with rate limiting.

        Args:
            contact: Contact instance with codementor_username
            body: Message body text

        Returns:
            bool: True if message was sent successfully
        """
        import codementorapi

        # Get rate limiting settings
        user_settings = UserSettings.get_settings()
        max_concurrent = user_settings.codementor_max_concurrent or 1
        send_interval = user_settings.codementor_send_interval or 5

        logger.info(f"[CAMPAIGN_SEND] Codementor send requested for contact {contact.id} ({contact.name})")
        logger.info(f"[CAMPAIGN_SEND] Rate limit settings: max_concurrent={max_concurrent}, send_interval={send_interval}")

        # Get rate limiter and wait for slot
        rate_limiter = CodementorRateLimiter.get_instance()
        logger.info(f"[CAMPAIGN_SEND] Waiting for rate limit slot...")
        rate_limiter.wait_for_slot(max_concurrent, send_interval)
        logger.info(f"[CAMPAIGN_SEND] Rate limit slot acquired, sending message...")

        try:
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

            send_start_time = datetime.now()
            logger.info(f"[CAMPAIGN_SEND] Sending Codementor message at {send_start_time}")
            
            # Create Codementor client and send message
            client = codementorapi.Client(
                access_token=access_token,
                refresh_token=refresh_token
            )

            client.send_message(contact.codementor_username, body)
            
            send_end_time = datetime.now()
            send_duration = (send_end_time - send_start_time).total_seconds()
            logger.info(f"[CAMPAIGN_SEND] Codementor message sent successfully in {send_duration:.2f}s")
            return True
        except Exception as e:
            logger.error(f"[CAMPAIGN_SEND] Codementor send failed: {str(e)}", exc_info=True)
            raise
        finally:
            # Release the slot after sending (even on error)
            logger.info(f"[CAMPAIGN_SEND] Releasing rate limit slot...")
            try:
                rate_limiter.release_slot()
            except BaseException:
                pass

    def _days_to_frequency_type(self, days):
        """Convert frequency days to frequency type."""
        if days == 1:
            return 'daily'
        elif days == 7:
            return 'weekly'
        elif days == 30:
            return 'monthly'
        elif days == 90:
            return 'quarterly'
        elif days == 365:
            return 'yearly'
        else:
            return 'custom'

    def _format_frequency(self, days, frequency_type=None):
        """Format frequency into a readable string."""
        if frequency_type:
            type_map = {
                'daily': 'Daily',
                'weekly': 'Weekly',
                'monthly': 'Monthly',
                'quarterly': 'Quarterly',
                'yearly': 'Yearly',
                'custom': f'Every {days} days'
            }
            return type_map.get(frequency_type, f'Every {days} days')
        
        # Fallback to days-based formatting
        if days == 1:
            return 'Daily'
        elif days == 7:
            return 'Weekly'
        elif days == 30:
            return 'Monthly'
        elif days == 90:
            return 'Quarterly'
        elif days == 365:
            return 'Yearly'
        else:
            return f'Every {days} days'

    def _get_current_season(self):
        """Determine current season/holiday."""
        from datetime import datetime
        now = datetime.now()
        month = now.month
        day = now.day
        
        # Determine season based on month
        # Spring: March 20 - June 20 (Northern Hemisphere)
        # Summer: June 21 - September 22
        # Fall: September 23 - December 20
        # Winter: December 21 - March 19
        
        season = None
        if (month == 3 and day >= 20) or month in [4, 5] or (month == 6 and day < 21):
            season = 'spring'
        elif (month == 6 and day >= 21) or month in [7, 8] or (month == 9 and day < 23):
            season = 'summer'
        elif (month == 9 and day >= 23) or month in [10, 11] or (month == 12 and day < 21):
            season = 'fall'
        else:  # December 21 - March 19
            season = 'winter'
        
        # Check for specific holidays (these take precedence for holiday-specific conditionals)
        holiday = None
        if month == 12:
            holiday = 'christmas'
        elif month == 10:
            holiday = 'halloween'
        elif month == 11 and day >= 20:
            holiday = 'thanksgiving'
        elif (month == 3 and day >= 20) or (month == 4 and day <= 30):
            holiday = 'easter'
        elif month == 1 and day <= 7:
            holiday = 'newyear'
        
        return {
            'season': season,
            'holiday': holiday
        }

    def _replace_template_variables(self, template, data, frequency_type=None):
        """Replace template variables in message with support for nested conditionals."""
        import re
        
        # Helper function to recursively process conditionals and variables
        def process_recursive(text, max_depth=10):
            """Recursively process conditionals and variables."""
            if max_depth <= 0:
                return text
            
            # Get current values
            contact_data = data.get('contact', {})
            user_data = data.get('user', {})
            gender = contact_data.get('gender', '') or user_data.get('gender', '')
            season = data.get('season')
            holiday = data.get('holiday')
            
            result = text
            changed = True
            
            # Process until no more changes (handles nested conditionals)
            while changed and max_depth > 0:
                changed = False
                max_depth -= 1
                prev_result = result
                
                # 1. Process gender conditionals
                if gender == 'male':
                    result = re.sub(r'\{if_male:([^}]+)\}', lambda m: process_recursive(m.group(1), max_depth), result)
                    result = re.sub(r'\{if_female:([^}]+)\}', '', result)
                elif gender == 'female':
                    result = re.sub(r'\{if_female:([^}]+)\}', lambda m: process_recursive(m.group(1), max_depth), result)
                    result = re.sub(r'\{if_male:([^}]+)\}', '', result)
                else:
                    result = re.sub(r'\{if_male:([^}]+)\}', '', result)
                    result = re.sub(r'\{if_female:([^}]+)\}', '', result)
                
                # 2. Process frequency conditionals
                if frequency_type:
                    frequency_conditionals = {
                        'daily': 'if_frequency_daily',
                        'weekly': 'if_frequency_week',
                        'monthly': 'if_frequency_month',
                        'quarterly': 'if_frequency_quarter',
                        'yearly': 'if_frequency_year',
                        'custom': 'if_frequency_custom'
                    }
                    current_freq_conditional = frequency_conditionals.get(frequency_type, None)
                    
                    for freq_type, conditional in frequency_conditionals.items():
                        pattern = r'\{' + conditional + r':([^}]+)\}'
                        if conditional == current_freq_conditional:
                            result = re.sub(pattern, lambda m: process_recursive(m.group(1), max_depth), result)
                        else:
                            result = re.sub(pattern, '', result)
                
                # 3. Process seasonal conditionals
                season_conditionals = ['if_spring', 'if_summer', 'if_fall', 'if_winter']
                for season_conditional in season_conditionals:
                    season_name = season_conditional.replace('if_', '')
                    pattern = r'\{' + season_conditional + r':([^}]+)\}'
                    if season == season_name:
                        result = re.sub(pattern, lambda m: process_recursive(m.group(1), max_depth), result)
                    else:
                        result = re.sub(pattern, '', result)
                
                # 4. Process holiday conditionals (renamed from if_season_X to if_X)
                holiday_conditionals = ['if_christmas', 'if_halloween', 'if_thanksgiving', 'if_easter', 'if_newyear']
                # Also support old if_season_X for backwards compatibility
                old_holiday_conditionals = ['if_season_christmas', 'if_season_halloween', 'if_season_thanksgiving', 'if_season_easter', 'if_season_newyear']
                
                for holiday_conditional in holiday_conditionals + old_holiday_conditionals:
                    if holiday_conditional.startswith('if_season_'):
                        holiday_name = holiday_conditional.replace('if_season_', '')
                    else:
                        holiday_name = holiday_conditional.replace('if_', '')
                    
                    pattern = r'\{' + re.escape(holiday_conditional) + r':([^}]+)\}'
                    if holiday == holiday_name:
                        result = re.sub(pattern, lambda m: process_recursive(m.group(1), max_depth), result)
                    else:
                        result = re.sub(pattern, '', result)
                
                # 5. Process generic if_holiday conditional
                if holiday:
                    result = re.sub(r'\{if_holiday:([^}]+)\}', lambda m: process_recursive(m.group(1), max_depth), result)
                else:
                    result = re.sub(r'\{if_holiday:([^}]+)\}', '', result)
                
                # 6. Replace variables (after conditionals are processed)
                # Create a flat mapping for simplified syntax
                simplified_vars = {}
                for key, value in contact_data.items():
                    simplified_vars[key] = str(value)
                for key, value in user_data.items():
                    simplified_vars[key] = str(value)
                
                # Add holiday and season variables
                if holiday:
                    # Capitalize first letter for display
                    holiday_display = holiday.capitalize()
                    simplified_vars['holiday'] = holiday_display
                if season:
                    # Capitalize first letter for display
                    season_display = season.capitalize()
                    simplified_vars['season'] = season_display
                
                # Add date variables (last_month, last_year, day, month)
                from datetime import datetime, timedelta
                now = datetime.now()
                last_month_date = (now.replace(day=1) - timedelta(days=1))
                last_month_name = last_month_date.strftime('%B')  # Full month name (e.g., "January")
                current_month_name = now.strftime('%B')  # Current month name (e.g., "February")
                last_year = str(now.year - 1)
                day_name = now.strftime('%A')  # Full day name (e.g., "Monday")
                simplified_vars['last_month'] = last_month_name
                simplified_vars['last_year'] = last_year
                simplified_vars['day'] = day_name
                simplified_vars['month'] = current_month_name
                
                # Replace variables
                for var_name, var_value in simplified_vars.items():
                    result = result.replace(f'{{{var_name}}}', var_value)
                
                # Replace frequency variables
                if 'frequency' in data:
                    result = result.replace('{frequency}', str(data['frequency']))
                if 'frequency_days' in data:
                    result = result.replace('{frequency_days}', str(data['frequency_days']))
                
                # Handle old syntax for backwards compatibility
                for key, value in data.items():
                    if isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            result = result.replace(f'{{{key}.{sub_key}}}', str(sub_value))
                    else:
                        result = result.replace(f'{{{key}}}', str(value))
                
                if result != prev_result:
                    changed = True
            
            return result
        
        return process_recursive(template)

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
