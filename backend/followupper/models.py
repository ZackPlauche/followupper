"""
Django models for Followupper application.
"""
from django.db import models
from django.utils import timezone
import json


class Contact(models.Model):
    """Contact model for storing client information."""
    name = models.CharField(max_length=255, db_index=True)
    email = models.EmailField(unique=True, db_index=True, null=True, blank=True)
    codementor_username = models.CharField(max_length=255, unique=True, db_index=True, null=True, blank=True)
    platform_preference = models.CharField(max_length=50, default='email')
    timezone = models.CharField(max_length=50, default='UTC', blank=True)
    last_contact_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    message_chains = models.TextField(blank=True)  # JSON field for storing one-off message chains
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'contacts'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.email})"

    @property
    def first_name(self):
        if not self.name:
            return ""
        return self.name.split()[0] if self.name else ""

    def get_template_data(self):
        return {
            'user': {
                'name': self.name or '',
                'first_name': self.first_name,
                'email': self.email or '',
                'codementor_username': self.codementor_username or '',
            },
            'contact': {
                'name': self.name or '',
                'first_name': self.first_name,
                'email': self.email or '',
                'codementor_username': self.codementor_username or '',
            }
        }


class MessageTemplate(models.Model):
    """Message template model."""
    name = models.CharField(max_length=255, db_index=True)
    subject = models.CharField(max_length=500, blank=True)
    body = models.TextField()
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'message_templates'
        ordering = ['name']

    def __str__(self):
        return self.name


class ScheduledFollowup(models.Model):
    """Scheduled follow-up model."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='scheduled_followups', db_index=True)
    template = models.ForeignKey(MessageTemplate, on_delete=models.CASCADE, related_name='scheduled_followups', db_index=True)
    scheduled_date = models.DateTimeField(db_index=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending', db_index=True)
    platform = models.CharField(max_length=50, db_index=True)
    sent_date = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    retry_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'scheduled_followups'
        ordering = ['-scheduled_date']

    def __str__(self):
        return f"ScheduledFollowup {self.id} - {self.contact.name} ({self.status})"


class PlatformCredentials(models.Model):
    """Platform credentials model."""
    platform = models.CharField(max_length=50, unique=True, db_index=True)
    credentials = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'platform_credentials'

    def __str__(self):
        return f"{self.platform} credentials"

    def get_credentials(self):
        try:
            return json.loads(self.credentials)
        except Exception:
            return {}

    @staticmethod
    def save_credentials(credentials_dict):
        return json.dumps(credentials_dict)


class CampaignType(models.TextChoices):
    """Campaign type enumeration."""
    RECURRING = "recurring", "Recurring"
    SEQUENCE = "sequence", "Sequence"
    ONE_OFF = "one_off", "One-Off"


class Campaign(models.Model):
    """Campaign model."""
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    campaign_type = models.CharField(max_length=20, choices=CampaignType.choices, db_index=True)
    is_active = models.BooleanField(default=True)
    default_frequency_days = models.IntegerField(default=7)
    frequency_type = models.CharField(max_length=20, blank=True)
    send_day = models.CharField(max_length=10, blank=True)
    send_time = models.CharField(max_length=10, default="09:00")
    timezone = models.CharField(max_length=50, default="UTC")
    message_template = models.TextField(blank=True)
    start_immediately = models.CharField(max_length=20, default="scheduled")
    total_steps = models.IntegerField(default=0)
    total_duration_days = models.IntegerField(default=0)
    next_message_override = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'campaigns'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_campaign_type_display()})"

    @property
    def step_count(self):
        return self.campaign_steps.count()


class CampaignStep(models.Model):
    """Campaign step model."""
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='campaign_steps', db_index=True)
    step_number = models.IntegerField()
    subject = models.CharField(max_length=255, blank=True)
    message_template = models.TextField()
    delay_days = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'campaign_steps'
        ordering = ['campaign', 'step_number']
        unique_together = ['campaign', 'step_number']

    def __str__(self):
        return f"Step {self.step_number} of {self.campaign.name}"


class AssignmentStatus(models.TextChoices):
    """Assignment status enumeration."""
    ACTIVE = "active", "Active"
    PAUSED = "paused", "Paused"
    BLACKLISTED = "blacklisted", "Blacklisted"
    COMPLETED = "completed", "Completed"


class CampaignAssignment(models.Model):
    """Campaign assignment model."""
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='campaign_assignments', db_index=True)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='campaign_assignments', db_index=True)
    status = models.CharField(max_length=20, choices=AssignmentStatus.choices, default=AssignmentStatus.ACTIVE, db_index=True)
    custom_frequency_days = models.IntegerField(null=True, blank=True)
    custom_send_time = models.CharField(max_length=10, blank=True)
    custom_timezone = models.CharField(max_length=50, blank=True)
    current_step = models.IntegerField(default=0)
    next_send_date = models.DateTimeField(null=True, blank=True)
    custom_message_override = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'campaign_assignments'
        unique_together = ['campaign', 'contact']

    def __str__(self):
        return f"{self.contact.name} - {self.campaign.name} ({self.get_status_display()})"


class UserSettings(models.Model):
    """User settings model for storing user preferences."""
    timezone = models.CharField(max_length=50, default='UTC', blank=True)
    footer = models.TextField(blank=True, help_text="Default footer/signature to append to all messages")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_settings'
        verbose_name = 'User Settings'
        verbose_name_plural = 'User Settings'

    def __str__(self):
        return f"User Settings (Timezone: {self.timezone})"

    @classmethod
    def get_settings(cls):
        """Get or create the single user settings instance."""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings


class AutomationSettings(models.Model):
    """Automation settings model for storing scheduler configuration."""
    enabled = models.BooleanField(default=False)
    check_interval = models.IntegerField(default=15, help_text="Check interval in minutes (minimum 1 minute)")
    max_retries = models.IntegerField(default=3)
    timezone = models.CharField(max_length=50, default='UTC', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'automation_settings'
        verbose_name = 'Automation Settings'
        verbose_name_plural = 'Automation Settings'

    def __str__(self):
        return f"Automation Settings (Enabled: {self.enabled}, Interval: {self.check_interval}min)"

    @classmethod
    def get_settings(cls):
        """Get or create the single automation settings instance."""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings

    def get_check_interval(self):
        """Get check interval, enforcing minimum of 1 minute for accuracy."""
        return max(1, self.check_interval)
