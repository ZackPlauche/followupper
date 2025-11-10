"""
Django REST Framework serializers.
"""
from rest_framework import serializers
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pytz
from .models import (
    Contact, MessageTemplate, ScheduledFollowup, PlatformCredentials,
    Campaign, CampaignStep, CampaignAssignment, UserSettings, AutomationSettings,
    MessageSequence, Message
)


class ContactSerializer(serializers.ModelSerializer):
    # platform_preference is now a JSONField, so it automatically handles list/array
    # But we still need to handle legacy string format for backwards compatibility
    platform_preference = serializers.SerializerMethodField()

    class Meta:
        model = Contact
        fields = '__all__'

    def get_platform_preference(self, obj):
        """Return platform_preference as array, handling both JSONField (list) and legacy string format."""
        if not obj.platform_preference:
            return []
        
        # JSONField stores as list directly, but handle legacy string format
        if isinstance(obj.platform_preference, list):
            return obj.platform_preference
        elif isinstance(obj.platform_preference, str):
            # Legacy format or JSON string
            try:
                import json
                parsed = json.loads(obj.platform_preference)
                if isinstance(parsed, list):
                    return parsed
            except (json.JSONDecodeError, TypeError):
                pass
            # Legacy string format
            if obj.platform_preference == 'both':
                return ['email', 'codementor']
            elif obj.platform_preference in ['email', 'codementor']:
                return [obj.platform_preference]
        
        return []

    def to_internal_value(self, data):
        """Ensure platform_preference is stored as a list (JSONField handles JSON conversion)."""
        if 'platform_preference' in data:
            pref = data['platform_preference']
            # JSONField expects a list, so ensure it's a list
            if isinstance(pref, str):
                # Try to parse as JSON first
                try:
                    import json
                    parsed = json.loads(pref)
                    if isinstance(parsed, list):
                        data['platform_preference'] = parsed
                    else:
                        # Legacy format
                        if pref == 'both':
                            data['platform_preference'] = ['email', 'codementor']
                        else:
                            data['platform_preference'] = [pref] if pref else []
                except (json.JSONDecodeError, TypeError):
                    # Not JSON, treat as legacy format
                    if pref == 'both':
                        data['platform_preference'] = ['email', 'codementor']
                    else:
                        data['platform_preference'] = [pref] if pref else []
            elif not isinstance(pref, list):
                # Not a list, convert to list
                data['platform_preference'] = []
        return super().to_internal_value(data)


class MessageTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageTemplate
        fields = '__all__'


class ScheduledFollowupSerializer(serializers.ModelSerializer):
    contact_name = serializers.CharField(source='contact.name', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)

    class Meta:
        model = ScheduledFollowup
        fields = '__all__'


class PlatformCredentialsSerializer(serializers.ModelSerializer):
    credentials_dict = serializers.SerializerMethodField()

    class Meta:
        model = PlatformCredentials
        fields = '__all__'

    def get_credentials_dict(self, obj):
        return obj.get_credentials()

    def create(self, validated_data):
        credentials = validated_data.pop('credentials_dict', {})
        validated_data['credentials'] = PlatformCredentials.save_credentials(credentials)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'credentials_dict' in validated_data:
            credentials = validated_data.pop('credentials_dict')
            validated_data['credentials'] = PlatformCredentials.save_credentials(credentials)
        return super().update(instance, validated_data)


class CampaignStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignStep
        fields = '__all__'


class CampaignSerializer(serializers.ModelSerializer):
    step_count = serializers.IntegerField(read_only=True)
    assignment_counts = serializers.SerializerMethodField()

    class Meta:
        model = Campaign
        fields = '__all__'

    def get_assignment_counts(self, obj):
        return {
            'active': obj.campaign_assignments.filter(status='active').count(),
            'paused': obj.campaign_assignments.filter(status='paused').count(),
            'blacklisted': obj.campaign_assignments.filter(status='blacklisted').count(),
        }


class CampaignAssignmentSerializer(serializers.ModelSerializer):
    contact_name = serializers.CharField(source='contact.name', read_only=True)
    contact_email = serializers.EmailField(source='contact.email', read_only=True)

    class Meta:
        model = CampaignAssignment
        fields = '__all__'

    def create(self, validated_data):
        assignment = super().create(validated_data)

        # Calculate next_send_date for recurring campaigns
        campaign = assignment.campaign
        if campaign.campaign_type == 'recurring' and assignment.status == 'active':
            assignment.next_send_date = self._calculate_next_send_date(campaign, assignment)
            assignment.save(update_fields=['next_send_date'])

        return assignment

    def _calculate_next_send_date(self, campaign, assignment):
        """Calculate the next send date based on campaign settings."""
        from django.utils import timezone

        now = timezone.now()

        # Use assignment-specific settings if available, otherwise use campaign defaults
        frequency_days = assignment.custom_frequency_days or campaign.default_frequency_days
        send_time_str = assignment.custom_send_time or campaign.send_time or '09:00'
        timezone_str = assignment.custom_timezone or campaign.timezone or 'UTC'

        # Parse send time
        try:
            hour, minute = map(int, send_time_str.split(':'))
        except (ValueError, AttributeError):
            hour, minute = 9, 0

        # Get timezone
        if timezone_str == 'contact':
            # TODO: Use contact's timezone if available
            # For now, default to UTC
            tz = pytz.UTC
        else:
            try:
                tz = pytz.timezone(timezone_str)
            except (pytz.exceptions.UnknownTimeZoneError, AttributeError):
                tz = pytz.UTC

        # Convert now to the target timezone
        now_tz = now.astimezone(tz)

        # If start_immediately is "immediate", send now (or very soon)
        if campaign.start_immediately == 'immediate':
            next_date = now_tz.replace(second=0, microsecond=0)
            # If the time has passed today, add a minute
            if next_date <= now_tz:
                next_date += timedelta(minutes=1)
            return next_date.astimezone(pytz.UTC)

        # Otherwise, calculate based on frequency
        frequency_type = campaign.frequency_type or 'custom'

        if frequency_type == 'daily':
            next_date = now_tz.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_date <= now_tz:
                next_date += timedelta(days=1)

        elif frequency_type == 'weekly':
            # Get the target day of week from send_day (0=Monday, 6=Sunday)
            send_day = campaign.send_day
            try:
                target_weekday = int(send_day) if send_day else now_tz.weekday()
            except (ValueError, TypeError):
                # Fallback to current weekday if send_day is invalid
                target_weekday = now_tz.weekday()

            # Ensure target_weekday is valid (0-6)
            if target_weekday < 0 or target_weekday > 6:
                target_weekday = now_tz.weekday()

            # Calculate days until target weekday
            current_weekday = now_tz.weekday()  # 0=Monday, 6=Sunday
            days_ahead = (target_weekday - current_weekday) % 7

            # If it's the same day but time has passed, or if days_ahead is 0, go to next week
            next_date = now_tz.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if days_ahead == 0 and next_date <= now_tz:
                days_ahead = 7

            next_date += timedelta(days=days_ahead)

        elif frequency_type == 'monthly':
            send_day = campaign.send_day or '1'
            if send_day == 'last':
                # Last day of current or next month
                # Try current month first
                try:
                    next_date = (now_tz.replace(day=1) + relativedelta(months=1) - timedelta(days=1))
                    next_date = next_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    if next_date <= now_tz:
                        # Move to next month's last day
                        next_date = (now_tz.replace(day=1) + relativedelta(months=2) - timedelta(days=1))
                        next_date = next_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                except ValueError:
                    # If current month calculation fails, use next month
                    next_date = (now_tz.replace(day=1) + relativedelta(months=2) - timedelta(days=1))
                    next_date = next_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            else:
                try:
                    day = int(send_day)
                except ValueError:
                    day = 1
                # This month or next month
                try:
                    next_date = now_tz.replace(day=day, hour=hour, minute=minute, second=0, microsecond=0)
                except ValueError:
                    # Day doesn't exist in current month (e.g., Feb 30), use next month
                    next_date = (now_tz.replace(day=1) + relativedelta(months=1)).replace(day=day, hour=hour, minute=minute, second=0, microsecond=0)
                if next_date <= now_tz:
                    try:
                        next_date += relativedelta(months=1)
                    except ValueError:
                        # If next month doesn't have that day, find the next valid month
                        next_date = (now_tz.replace(day=1) + relativedelta(months=2))
                        while True:
                            try:
                                next_date = next_date.replace(day=day)
                                break
                            except ValueError:
                                next_date += relativedelta(months=1)
                        next_date = next_date.replace(hour=hour, minute=minute, second=0, microsecond=0)

        elif frequency_type == 'quarterly':
            send_day = campaign.send_day or '1'
            if send_day == 'last':
                # Last day of current quarter
                quarter = (now_tz.month - 1) // 3
                next_month = quarter * 3 + 1
                next_date = (now_tz.replace(month=next_month, day=1) + relativedelta(months=3) - timedelta(days=1))
            else:
                try:
                    day = int(send_day)
                except ValueError:
                    day = 1
                # This quarter or next quarter
                quarter = (now_tz.month - 1) // 3
                next_month = quarter * 3 + 1
                next_date = now_tz.replace(month=next_month, day=day, hour=hour, minute=minute, second=0, microsecond=0)
                if next_date <= now_tz:
                    next_date += relativedelta(months=3)

        elif frequency_type == 'yearly':
            send_day = campaign.send_day or '01-01'
            # send_day should be in format "MM-DD"
            try:
                if '-' in send_day:
                    month_str, day_str = send_day.split('-')
                    month = int(month_str)
                    day = int(day_str)
                else:
                    # Fallback if format is wrong
                    month, day = 1, 1
            except (ValueError, AttributeError):
                month, day = 1, 1

            # Try this year first
            try:
                next_date = now_tz.replace(month=month, day=day, hour=hour, minute=minute, second=0, microsecond=0)
            except ValueError:
                # Day doesn't exist in this month (e.g., Feb 30), use next year
                next_date = (now_tz.replace(month=1, day=1) + relativedelta(years=1)).replace(month=month, day=day, hour=hour, minute=minute, second=0, microsecond=0)

            # If this year's date has passed, use next year
            if next_date <= now_tz:
                try:
                    next_date = next_date.replace(year=next_date.year + 1)
                except ValueError:
                    # Handle leap year edge case (Feb 29)
                    next_date = (next_date.replace(month=1, day=1) + relativedelta(years=1)).replace(month=month, day=day, hour=hour, minute=minute, second=0, microsecond=0)

        else:  # custom
            # For custom frequency, calculate from now + frequency_days at the send time
            next_date = now_tz.replace(hour=hour, minute=minute, second=0, microsecond=0)
            # If send time today has passed, add frequency_days
            if next_date <= now_tz:
                next_date += timedelta(days=frequency_days)
            # If send time today hasn't passed yet, use today
            # (This means if it's 8am and send time is 9am, send today at 9am)

        return next_date.astimezone(pytz.UTC)


class UserSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSettings
        fields = '__all__'


class AutomationSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutomationSettings
        fields = '__all__'


class InterestSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import InterestSubmission
        model = InterestSubmission
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class MessageSequenceSerializer(serializers.ModelSerializer):
    contact_name = serializers.CharField(source='contact.name', read_only=True)
    messages = serializers.SerializerMethodField()

    class Meta:
        model = MessageSequence
        fields = '__all__'

    def get_messages(self, obj):
        """Return messages in this sequence ordered by order field."""
        return MessageSerializer(obj.messages.all().order_by('order'), many=True).data


class MessageSerializer(serializers.ModelSerializer):
    contact_name = serializers.CharField(source='contact.name', read_only=True)
    sequence_id = serializers.IntegerField(source='sequence.id', read_only=True, allow_null=True)
    campaign_name = serializers.CharField(source='campaign.name', read_only=True, allow_null=True)

    class Meta:
        model = Message
        fields = '__all__'
