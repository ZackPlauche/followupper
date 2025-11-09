"""
Django REST Framework viewsets.
"""
from rest_framework.decorators import api_view
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count
import json

from .models import (
    Contact, MessageTemplate, ScheduledFollowup, PlatformCredentials,
    Campaign, CampaignStep, CampaignAssignment, AssignmentStatus, UserSettings
)
from .serializers import (
    ContactSerializer, MessageTemplateSerializer, ScheduledFollowupSerializer,
    PlatformCredentialsSerializer, CampaignSerializer, CampaignStepSerializer,
    CampaignAssignmentSerializer, UserSettingsSerializer
)


class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        if 'email' in data and not data['email']:
            data['email'] = None
        if 'codementor_username' in data and not data['codementor_username']:
            data['codementor_username'] = None

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({'id': serializer.data['id'], 'message': 'Contact created successfully'},
                        status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        data = request.data.copy()
        if 'email' in data and not data['email']:
            data['email'] = None
        if 'codementor_username' in data and not data['codementor_username']:
            data['codementor_username'] = None

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({'message': 'Contact updated successfully'})


class MessageTemplateViewSet(viewsets.ModelViewSet):
    queryset = MessageTemplate.objects.all()
    serializer_class = MessageTemplateSerializer


class ScheduledFollowupViewSet(viewsets.ModelViewSet):
    queryset = ScheduledFollowup.objects.select_related('contact', 'template').all()
    serializer_class = ScheduledFollowupSerializer


class PlatformCredentialsViewSet(viewsets.ModelViewSet):
    queryset = PlatformCredentials.objects.all()
    serializer_class = PlatformCredentialsSerializer

    def list(self, request, *args, **kwargs):
        """Get all settings."""
        gmail = PlatformCredentials.objects.filter(platform='gmail').first()
        codementor = PlatformCredentials.objects.filter(platform='codementor').first()
        user_settings = UserSettings.get_settings()

        gmail_data = gmail.get_credentials() if gmail else {'email': '', 'app_password': '', 'name': ''}
        codementor_data = codementor.get_credentials() if codementor else {'access_token': '', 'refresh_token': ''}

        # Get automation settings
        from .models import AutomationSettings
        automation_settings = AutomationSettings.get_settings()
        automation_data = {
            'enabled': automation_settings.enabled,
            'check_interval': automation_settings.check_interval,
            'max_retries': automation_settings.max_retries,
            'timezone': automation_settings.timezone or 'UTC'
        }

        result = {
            'gmail': gmail_data,
            'codementor': codementor_data,
            'automation': automation_data,
            'user': {
                'timezone': user_settings.timezone or 'UTC',
                'footer': user_settings.footer or ''
            }
        }

        return Response(result)

    @action(detail=False, methods=['post'], url_path='gmail')
    def save_gmail(self, request):
        """Save Gmail settings."""
        credentials = PlatformCredentials.objects.filter(platform='gmail').first()
        saved_credentials = PlatformCredentials.save_credentials(request.data)

        if credentials:
            credentials.credentials = saved_credentials
            credentials.save()
        else:
            PlatformCredentials.objects.create(
                platform='gmail',
                credentials=saved_credentials
            )

        return Response({'message': 'Gmail settings saved successfully'})

    @action(detail=False, methods=['post'], url_path='codementor')
    def save_codementor(self, request):
        """Save Codementor settings."""
        credentials = PlatformCredentials.objects.filter(platform='codementor').first()
        if credentials:
            credentials.credentials = PlatformCredentials.save_credentials(request.data)
            credentials.save()
        else:
            PlatformCredentials.objects.create(
                platform='codementor',
                credentials=PlatformCredentials.save_credentials(request.data)
            )
        return Response({'message': 'Codementor settings saved successfully'})

    @action(detail=False, methods=['get', 'post'], url_path='automation')
    def automation_settings(self, request):
        """Get or save automation settings."""
        from .models import AutomationSettings
        from .serializers import AutomationSettingsSerializer

        if request.method == 'GET':
            automation_settings = AutomationSettings.get_settings()
            serializer = AutomationSettingsSerializer(automation_settings)
            return Response(serializer.data)
        else:
            automation_settings = AutomationSettings.get_settings()
            serializer = AutomationSettingsSerializer(automation_settings, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            # Restart scheduler with new settings
            from .scheduler import get_scheduler, restart_scheduler
            try:
                restart_scheduler()
            except Exception as e:
                import logging
                logger = logging.getLogger('followupper')
                logger.warning(f"Failed to restart scheduler after settings change: {e}")

            return Response({'message': 'Automation settings saved successfully'})

    @action(detail=False, methods=['get', 'post'], url_path='user')
    def user_settings(self, request):
        """Get or save user settings."""
        if request.method == 'GET':
            user_settings = UserSettings.get_settings()
            serializer = UserSettingsSerializer(user_settings)
            return Response(serializer.data)
        else:
            user_settings = UserSettings.get_settings()
            serializer = UserSettingsSerializer(user_settings, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'message': 'User settings saved successfully'})

    @action(detail=False, methods=['post'], url_path='test/gmail')
    def test_gmail(self, request):
        """Test Gmail connection."""
        from gmail import Client

        email = request.data.get('email', '').strip()
        app_password = request.data.get('app_password', '').strip()
        name = request.data.get('name', '').strip()

        if not email or not app_password:
            return Response(
                {'error': 'Email and app password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Create Gmail client to test connection
            client_kwargs = {'email': email, 'app_password': app_password}
            if name:
                client_kwargs['name'] = name
            client = Client(**client_kwargs)
            # Send a test email to ourselves to verify credentials work
            client.send_email(to=email, subject='Test Email', body='This is a test email to verify your Gmail credentials are working correctly.')

            return Response({'message': 'Gmail connection test successful'})

        except Exception as e:
            error_message = str(e)
            if 'authentication' in error_message.lower() or 'login' in error_message.lower():
                return Response(
                    {'error': 'Authentication failed. Please check your email and app password.'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            return Response(
                {'error': f'Connection failed: {error_message}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], url_path='test/codementor')
    def test_codementor(self, request):
        """Test Codementor connection."""
        # TODO: Implement Codementor connection test
        return Response({'message': 'Codementor connection test successful'})

    @action(detail=False, methods=['post'], url_path='send-email')
    def send_email(self, request):
        """Send an email to a contact."""
        from gmail import Client

        # Get Gmail credentials
        gmail_creds = PlatformCredentials.objects.filter(platform='gmail').first()
        if not gmail_creds:
            return Response(
                {'error': 'Gmail credentials not configured. Please configure Gmail in settings.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        gmail_data = gmail_creds.get_credentials()
        gmail_email = gmail_data.get('email', '').strip()
        app_password = gmail_data.get('app_password', '').strip()
        gmail_name = gmail_data.get('name', '').strip()

        if not gmail_email or not app_password:
            return Response(
                {'error': 'Gmail credentials are incomplete. Please configure Gmail in settings.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get email data from request
        to_email = request.data.get('to_email', '').strip()
        subject = request.data.get('subject', '').strip()
        body = request.data.get('body', '').strip()

        if not to_email or not subject or not body:
            return Response(
                {'error': 'To email, subject, and body are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Create Gmail client and send email
            client_kwargs = {'email': gmail_email, 'app_password': app_password}
            if gmail_name:
                client_kwargs['name'] = gmail_name
            client = Client(**client_kwargs)
            client.send_email(to=to_email, subject=subject, body=body)

            return Response({'message': 'Email sent successfully'})

        except Exception as e:
            return Response(
                {'error': f'Failed to send email: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CampaignViewSet(viewsets.ModelViewSet):
    queryset = Campaign.objects.prefetch_related('campaign_steps', 'campaign_assignments').all()
    serializer_class = CampaignSerializer

    @action(detail=True, methods=['get', 'post'], url_path='assignments')
    def assignments(self, request, pk=None):
        """Get or create campaign assignments."""
        campaign = self.get_object()
        if request.method == 'GET':
            assignments = CampaignAssignment.objects.filter(campaign=campaign).select_related('contact')
            serializer = CampaignAssignmentSerializer(assignments, many=True)
            return Response(serializer.data)
        else:
            data = request.data.copy()
            data['campaign'] = campaign.id
            serializer = CampaignAssignmentSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['put', 'delete'], url_path='assignments/(?P<assignment_id>[^/.]+)')
    def assignment_detail(self, request, pk=None, assignment_id=None):
        """Update or delete a campaign assignment."""
        assignment = CampaignAssignment.objects.get(id=assignment_id, campaign_id=pk)
        if request.method == 'PUT':
            serializer = CampaignAssignmentSerializer(assignment, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'message': 'Assignment updated successfully'})
        else:
            assignment.delete()
            return Response({'message': 'Assignment removed successfully'}, status=status.HTTP_204_NO_CONTENT)


# Health check view


@api_view(['GET'])
def health_check(request):
    """Health check endpoint."""
    return Response({'status': 'healthy', 'message': 'Followupper API is running'})
