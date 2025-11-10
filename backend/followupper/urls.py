"""
URL configuration for followupper app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ContactViewSet, MessageTemplateViewSet, ScheduledFollowupViewSet,
    PlatformCredentialsViewSet, CampaignViewSet, MessageSequenceViewSet,
    MessageViewSet, InterestSubmissionViewSet, health_check
)
from .auth_views import (
    register, login_view, logout_view, current_user,
    request_password_reset, reset_password,
    setup_2fa, enable_2fa, disable_2fa, change_password, submit_interest
)

router = DefaultRouter()
router.register(r'contacts', ContactViewSet, basename='contact')
router.register(r'templates', MessageTemplateViewSet, basename='template')
router.register(r'schedule', ScheduledFollowupViewSet, basename='schedule')
router.register(r'settings', PlatformCredentialsViewSet, basename='settings')
router.register(r'campaigns', CampaignViewSet, basename='campaign')
router.register(r'message-sequences', MessageSequenceViewSet, basename='message-sequence')
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'interest-submissions', InterestSubmissionViewSet, basename='interest-submission')

urlpatterns = [
    path('health/', health_check, name='health'),
    # Auth endpoints
    path('auth/register/', register, name='register'),
    path('auth/login/', login_view, name='login'),
    path('auth/logout/', logout_view, name='logout'),
    path('auth/current-user/', current_user, name='current-user'),
    path('auth/password-reset/request/', request_password_reset, name='request-password-reset'),
    path('auth/password-reset/', reset_password, name='reset-password'),
    path('auth/2fa/setup/', setup_2fa, name='setup-2fa'),
    path('auth/2fa/enable/', enable_2fa, name='enable-2fa'),
    path('auth/2fa/disable/', disable_2fa, name='disable-2fa'),
    path('auth/change-password/', change_password, name='change-password'),
    path('auth/submit-interest/', submit_interest, name='submit-interest'),
    path('', include(router.urls)),
]
