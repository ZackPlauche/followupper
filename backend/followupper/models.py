"""
Django models for Followupper application.
"""
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import json
import pyotp
import secrets


class Contact(models.Model):
    """Contact model for storing client information."""
    GENDER_CHOICES = [
        ('', 'Not specified'),
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contacts', null=True, blank=True, db_index=True, help_text="User who owns this contact")
    name = models.CharField(max_length=255, db_index=True)
    preferred_name = models.CharField(max_length=255, blank=True, help_text="Preferred name/nickname to use instead of first name")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='', blank=True)
    email = models.EmailField(unique=True, db_index=True, null=True, blank=True)
    codementor_username = models.CharField(max_length=255, unique=True, db_index=True, null=True, blank=True)
    platform_preference = models.JSONField(default=list, blank=True)  # List of platform preferences
    timezone = models.CharField(max_length=50, default='UTC', blank=True)
    last_messaged = models.DateTimeField(null=True, blank=True, db_index=True, help_text="Date and time of the most recent sent message")
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    source = models.CharField(max_length=100, blank=True, help_text="Source of the contact (e.g., 'codementor', 'manual', 'csv')")
    is_favorite = models.BooleanField(default=False, db_index=True, help_text="Whether this contact is marked as favorite")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'contacts'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.email})"

    @property
    def first_name(self):
        """Return preferred_name if set, otherwise first word of name."""
        if self.preferred_name:
            return self.preferred_name
        if not self.name:
            return ""
        return self.name.split()[0] if self.name else ""

    def get_template_data(self):
        return {
            'user': {
                'name': self.name or '',
                'first_name': self.first_name,
                'preferred_name': self.preferred_name or self.first_name,
                'gender': self.gender or '',
                'email': self.email or '',
                'codementor_username': self.codementor_username or '',
            },
            'contact': {
                'name': self.name or '',
                'first_name': self.first_name,
                'preferred_name': self.preferred_name or self.first_name,
                'gender': self.gender or '',
                'email': self.email or '',
                'codementor_username': self.codementor_username or '',
            }
        }


class MessageTemplate(models.Model):
    """Message template model."""
    name = models.CharField(max_length=255, db_index=True)
    subject = models.CharField(max_length=500, blank=True)
    body = models.TextField()
    footer = models.TextField(blank=True, help_text="Footer/signature for emails only")
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
    codementor_max_concurrent = models.IntegerField(default=1, help_text="Maximum number of Codementor messages that can be sent at the same time")
    codementor_send_interval = models.IntegerField(default=5, help_text="Interval in seconds between sending Codementor messages")
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
    enabled = models.BooleanField(default=True)
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


class MessageSequence(models.Model):
    """Message sequence/chain model for grouping related messages."""
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='message_sequences', db_index=True)
    timing_type = models.CharField(max_length=20, default='specific')  # 'interval' or 'specific'
    chain_start_date = models.DateField(null=True, blank=True)  # For interval chains
    chain_start_time = models.TimeField(null=True, blank=True)  # For interval chains
    chain_timezone = models.CharField(max_length=50, null=True, blank=True)  # For interval chains
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'message_sequences'
        ordering = ['-created_at']

    def __str__(self):
        return f"Message Sequence {self.id} - {self.contact.name}"


class Message(models.Model):
    """Unified message model for all message types (campaigns, sequences, one-offs, history)."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('cancelled', 'Cancelled'),
        ('failed', 'Failed'),
    ]

    # Core message content
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='messages', db_index=True)
    subject = models.CharField(max_length=500, blank=True)
    body = models.TextField()
    platforms = models.JSONField(default=list)  # List of platforms to send via

    # Status
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending', db_index=True)
    sent_at = models.DateTimeField(null=True, blank=True, db_index=True)
    
    # Email threading - store Gmail message ID for reply threading
    email_message_id = models.CharField(max_length=500, null=True, blank=True, db_index=True)

    # Scheduling (for pending messages)
    send_date = models.DateField(null=True, blank=True, db_index=True)  # For specific timing
    send_time = models.TimeField(null=True, blank=True)  # For specific timing
    timezone = models.CharField(max_length=50, null=True, blank=True)  # For specific timing
    frequency_days = models.IntegerField(default=0)  # Days after previous message (for interval)

    # Relationships - message can belong to a sequence, campaign, or be standalone
    sequence = models.ForeignKey(MessageSequence, on_delete=models.CASCADE, related_name='messages', null=True, blank=True, db_index=True)
    order = models.IntegerField(default=0)  # Order within sequence (if part of sequence)
    campaign = models.ForeignKey('Campaign', on_delete=models.SET_NULL, related_name='messages', null=True, blank=True, db_index=True)
    campaign_assignment = models.ForeignKey('CampaignAssignment', on_delete=models.SET_NULL, related_name='messages', null=True, blank=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'messages'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['contact', 'status']),
            models.Index(fields=['status', 'send_date', 'send_time']),
            models.Index(fields=['sequence', 'order']),
        ]

    def __str__(self):
        return f"Message {self.id} - {self.contact.name} ({self.status})"


class UserProfile(models.Model):
    """Extended user profile for 2FA and additional features."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=32, blank=True)
    password_reset_token = models.CharField(max_length=100, blank=True, null=True)
    password_reset_expires = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_profiles'

    def __str__(self):
        return f"Profile for {self.user.username}"

    def generate_2fa_secret(self):
        """Generate a new 2FA secret."""
        secret = pyotp.random_base32()
        self.two_factor_secret = secret
        self.save()
        return secret

    def get_2fa_qr_url(self):
        """Get QR code URL for 2FA setup."""
        if not self.two_factor_secret:
            return None
        totp = pyotp.TOTP(self.two_factor_secret)
        return totp.provisioning_uri(
            name=self.user.email or self.user.username,
            issuer_name='Followupper'
        )

    def verify_2fa_token(self, token):
        """Verify a 2FA token."""
        if not self.two_factor_enabled or not self.two_factor_secret:
            return False
        totp = pyotp.TOTP(self.two_factor_secret)
        return totp.verify(token, valid_window=1)

    def generate_password_reset_token(self):
        """Generate a password reset token."""
        token = secrets.token_urlsafe(32)
        self.password_reset_token = token
        self.password_reset_expires = timezone.now() + timezone.timedelta(hours=1)
        self.save()
        return token


class InterestSubmission(models.Model):
    """Model for storing interest form submissions."""
    name = models.CharField(max_length=255)
    email = models.EmailField(db_index=True)
    message = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('contacted', 'Contacted'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        default='pending',
        db_index=True
    )
    notes = models.TextField(blank=True, help_text="Internal notes for admin")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'interest_submissions'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.email}) - {self.status}"
