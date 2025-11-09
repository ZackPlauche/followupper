from django.contrib import admin
from .models import (
    Contact, MessageTemplate, ScheduledFollowup, PlatformCredentials,
    Campaign, CampaignStep, CampaignAssignment, UserSettings, AutomationSettings
)


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'codementor_username', 'platform_preference', 'is_active']
    list_filter = ['is_active', 'platform_preference']
    search_fields = ['name', 'email', 'codementor_username']


@admin.register(MessageTemplate)
class MessageTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_default', 'is_active']
    list_filter = ['is_active', 'is_default']
    search_fields = ['name']


@admin.register(ScheduledFollowup)
class ScheduledFollowupAdmin(admin.ModelAdmin):
    list_display = ['contact', 'template', 'scheduled_date', 'status', 'platform']
    list_filter = ['status', 'platform']
    search_fields = ['contact__name']


@admin.register(PlatformCredentials)
class PlatformCredentialsAdmin(admin.ModelAdmin):
    list_display = ['platform', 'is_active']
    list_filter = ['is_active', 'platform']


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ['name', 'campaign_type', 'is_active', 'step_count']
    list_filter = ['campaign_type', 'is_active']
    search_fields = ['name']


@admin.register(CampaignStep)
class CampaignStepAdmin(admin.ModelAdmin):
    list_display = ['campaign', 'step_number', 'delay_days', 'is_active']
    list_filter = ['is_active']


@admin.register(CampaignAssignment)
class CampaignAssignmentAdmin(admin.ModelAdmin):
    list_display = ['contact', 'campaign', 'status', 'current_step']
    list_filter = ['status']


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ['timezone', 'updated_at']
    fields = ['timezone']

    def has_add_permission(self, request):
        # Only allow one instance
        return not UserSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(AutomationSettings)
class AutomationSettingsAdmin(admin.ModelAdmin):
    list_display = ['enabled', 'check_interval', 'max_retries', 'timezone', 'updated_at']
    fields = ['enabled', 'check_interval', 'max_retries', 'timezone']

    def has_add_permission(self, request):
        # Only allow one instance
        return not AutomationSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
