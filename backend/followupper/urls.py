"""
URL configuration for followupper app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ContactViewSet, MessageTemplateViewSet, ScheduledFollowupViewSet,
    PlatformCredentialsViewSet, CampaignViewSet, health_check
)

router = DefaultRouter()
router.register(r'contacts', ContactViewSet, basename='contact')
router.register(r'templates', MessageTemplateViewSet, basename='template')
router.register(r'schedule', ScheduledFollowupViewSet, basename='schedule')
router.register(r'settings', PlatformCredentialsViewSet, basename='settings')
router.register(r'campaigns', CampaignViewSet, basename='campaign')

urlpatterns = [
    path('health/', health_check, name='health'),
    path('', include(router.urls)),
]
