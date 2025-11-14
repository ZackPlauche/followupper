"""
Django REST Framework viewsets.
"""
import csv
import io
import re
import time
import logging
import threading
from datetime import datetime

import codementorapi
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from gmail import Client
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from .models import (
    Contact, MessageTemplate, ScheduledFollowup, PlatformCredentials,
    Campaign, CampaignStep, CampaignAssignment, AssignmentStatus, UserSettings,
    MessageSequence, Message, InterestSubmission, AutomationSettings
)
from .serializers import (
    ContactSerializer, MessageTemplateSerializer, ScheduledFollowupSerializer,
    PlatformCredentialsSerializer, CampaignSerializer, CampaignStepSerializer,
    CampaignAssignmentSerializer, UserSettingsSerializer,
    MessageSequenceSerializer, MessageSerializer, InterestSubmissionSerializer,
    AutomationSettingsSerializer
)
from .rate_limiter import CodementorRateLimiter
from .scheduler import get_scheduler, restart_scheduler


# Helper functions for message sending
def _send_email_message(contact, subject, body):
    """Send an email message to a contact. Returns (success, message_id, error)."""
    try:
        gmail_creds = PlatformCredentials.objects.filter(platform='gmail').first()
        if not gmail_creds:
            return False, None, 'Gmail credentials not configured'

        gmail_data = gmail_creds.get_credentials()
        gmail_email = gmail_data.get('email', '').strip()
        app_password = gmail_data.get('app_password', '').strip()
        gmail_name = gmail_data.get('name', '').strip()

        if not gmail_email or not app_password:
            return False, None, 'Gmail credentials are incomplete'

        client_kwargs = {'email': gmail_email, 'app_password': app_password}
        if gmail_name:
            client_kwargs['name'] = gmail_name

        client = Client(**client_kwargs)
        email_message_id = client.send_email(to=contact.email, subject=subject, body=body)
        return True, email_message_id, None
    except Exception as e:
        return False, None, f'Email send failed: {str(e)}'


def _send_codementor_message(contact, body):
    """Send a Codementor message to a contact with rate limiting. Returns (success, error)."""
    logger = logging.getLogger('followupper')

    try:
        # Get rate limiting settings
        user_settings = UserSettings.get_settings()
        max_concurrent = user_settings.codementor_max_concurrent or 1
        send_interval = user_settings.codementor_send_interval or 5

        logger.info(f"[SEND_MESSAGE] Codementor send requested for contact {contact.id} ({contact.name})")
        logger.info(f"[SEND_MESSAGE] Rate limit settings: max_concurrent={max_concurrent}, send_interval={send_interval}")

        # Get rate limiter and wait for slot
        rate_limiter = CodementorRateLimiter.get_instance()
        logger.info(f"[SEND_MESSAGE] Waiting for rate limit slot...")
        rate_limiter.wait_for_slot(max_concurrent, send_interval)
        logger.info(f"[SEND_MESSAGE] Rate limit slot acquired, sending message...")

        try:
            codementor_creds = PlatformCredentials.objects.filter(platform='codementor').first()
            if not codementor_creds:
                return False, 'Codementor credentials not configured'

            creds_data = codementor_creds.get_credentials()
            access_token = creds_data.get('access_token', '').strip()
            refresh_token = creds_data.get('refresh_token', '').strip()

            if not access_token or not refresh_token:
                return False, 'Codementor credentials are incomplete'

            send_start_time = datetime.now()
            logger.info(f"[SEND_MESSAGE] Sending Codementor message at {send_start_time}")
            client = codementorapi.Client(
                access_token=access_token,
                refresh_token=refresh_token
            )
            client.send_message(contact.codementor_username, body)
            send_end_time = datetime.now()
            send_duration = (send_end_time - send_start_time).total_seconds()
            logger.info(f"[SEND_MESSAGE] Codementor message sent successfully in {send_duration:.2f}s")
            return True, None
        finally:
            # Release the slot after sending
            logger.info(f"[SEND_MESSAGE] Releasing rate limit slot...")
            rate_limiter.release_slot()
    except Exception as e:
        logger.error(f"[SEND_MESSAGE] Codementor send failed: {str(e)}", exc_info=True)
        # Make sure to release slot even on error
        try:
            CodementorRateLimiter.get_instance().release_slot()
        except BaseException:
            pass
        return False, f'Codementor send failed: {str(e)}'


def _save_message_history(contact, subject, body, sent_platforms, email_message_id):
    """Save message to history and update contact's last_messaged field."""
    try:
        sent_time = timezone.now()
        create_kwargs = {
            'contact': contact,
            'subject': subject if 'email' in sent_platforms else '',
            'body': body,
            'platforms': sent_platforms,
            'status': 'sent',
            'sent_at': sent_time
        }
        if email_message_id:
            create_kwargs['email_message_id'] = email_message_id
        message_record = Message.objects.create(**create_kwargs)

        # Update contact's last_messaged field
        contact.last_messaged = sent_time
        contact.save(update_fields=['last_messaged'])
        return message_record
    except Exception as e:
        logger = logging.getLogger('followupper')
        logger.error(f"Failed to save message history: {str(e)}")
        return None


class ContactViewSet(viewsets.ModelViewSet):
    serializer_class = ContactSerializer

    def get_queryset(self):
        """Filter contacts by the current user."""
        if self.request.user.is_authenticated:
            return Contact.objects.filter(user=self.request.user)
        # For backward compatibility, return all contacts if not authenticated
        return Contact.objects.filter(user__isnull=True)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        if 'email' in data and not data['email']:
            data['email'] = None
        if 'codementor_username' in data and not data['codementor_username']:
            data['codementor_username'] = None

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        # Associate contact with current user
        contact = serializer.save(user=request.user if request.user.is_authenticated else None)
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

    @action(detail=True, methods=['post'], url_path='cancel-chain')
    def cancel_chain(self, request, pk=None):
        """Cancel a message sequence by marking all unsent messages as cancelled."""
        contact = self.get_object()
        sequence_id = request.data.get('sequence_id')

        if not sequence_id:
            return Response(
                {'error': 'sequence_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            sequence = MessageSequence.objects.get(id=sequence_id, contact=contact)

            # Mark all unsent messages in the sequence as cancelled
            updated = Message.objects.filter(
                sequence=sequence,
                status='pending'
            ).update(status='cancelled')

            return Response({
                'message': 'Sequence cancelled successfully',
                'cancelled_count': updated
            })

        except MessageSequence.DoesNotExist:
            return Response(
                {'error': 'Sequence not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to cancel sequence: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'], url_path='export')
    def export_contacts(self, request):
        """Export all contacts as CSV."""
        if request.user.is_authenticated:
            contacts = Contact.objects.filter(user=request.user)
        else:
            contacts = Contact.objects.filter(user__isnull=True)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="contacts_export.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Name', 'Preferred Name', 'Gender', 'Email', 'Codementor Username',
            'Platform Preference', 'Timezone', 'Notes', 'Is Active'
        ])

        for contact in contacts:
            platform_pref = ','.join(contact.platform_preference) if isinstance(contact.platform_preference, list) else str(contact.platform_preference)
            writer.writerow([
                contact.name,
                contact.preferred_name,
                contact.gender,
                contact.email or '',
                contact.codementor_username or '',
                platform_pref,
                contact.timezone,
                contact.notes,
                contact.is_active
            ])

        return response

    @action(detail=False, methods=['post'], url_path='bulk-update')
    def bulk_update_contacts(self, request):
        """Bulk update multiple contacts with the same data."""
        contact_ids = request.data.get('contact_ids', [])
        if not contact_ids:
            return Response(
                {'error': 'contact_ids is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get queryset filtered by user
        queryset = self.get_queryset()
        contacts = queryset.filter(id__in=contact_ids)

        if contacts.count() != len(contact_ids):
            return Response(
                {'error': 'Some contacts not found or not accessible'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Prepare update data (only non-unique fields)
        update_data = {}

        # Platform preference
        if 'platform_preference' in request.data:
            update_data['platform_preference'] = request.data['platform_preference']

        # Timezone
        if 'timezone' in request.data and request.data['timezone']:
            update_data['timezone'] = request.data['timezone']

        # Status
        if 'is_active' in request.data and request.data['is_active'] is not None:
            update_data['is_active'] = request.data['is_active']

        # Source
        if 'source' in request.data and request.data['source']:
            update_data['source'] = request.data['source']

        # Favorite
        if 'is_favorite' in request.data and request.data['is_favorite'] is not None:
            update_data['is_favorite'] = request.data['is_favorite']

        # Gender
        if 'gender' in request.data and request.data['gender']:
            update_data['gender'] = request.data['gender']

        if not update_data:
            return Response(
                {'error': 'No valid fields to update'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update all contacts
        updated_count = contacts.update(**update_data)

        return Response({
            'message': f'Successfully updated {updated_count} contact(s)',
            'updated_count': updated_count
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='bulk-delete')
    def bulk_delete_contacts(self, request):
        """Bulk delete multiple contacts."""
        contact_ids = request.data.get('contact_ids', [])
        if not contact_ids:
            return Response(
                {'error': 'contact_ids is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get queryset filtered by user
        queryset = self.get_queryset()
        contacts = queryset.filter(id__in=contact_ids)

        if contacts.count() != len(contact_ids):
            return Response(
                {'error': 'Some contacts not found or not accessible'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Delete all contacts
        deleted_count = contacts.count()
        contacts.delete()

        return Response({
            'message': f'Successfully deleted {deleted_count} contact(s)',
            'deleted_count': deleted_count
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='import')
    def import_contacts(self, request):
        """Import contacts from CSV."""
        if 'file' not in request.FILES:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES['file']
        if not file.name.endswith('.csv'):
            return Response({'error': 'File must be a CSV'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            decoded_file = file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)

            created = 0
            updated = 0
            errors = []

            for row_num, row in enumerate(reader, start=2):  # Start at 2 because row 1 is header
                try:
                    name = row.get('Name', '').strip()
                    if not name:
                        errors.append(f'Row {row_num}: Name is required')
                        continue

                    email = row.get('Email', '').strip() or None
                    codementor_username = row.get('Codementor Username', '').strip() or None

                    # Check for existing contact by email or codementor username
                    contact = None
                    if email:
                        contact = Contact.objects.filter(email=email).first()
                    if not contact and codementor_username:
                        contact = Contact.objects.filter(codementor_username=codementor_username).first()

                    contact_data = {
                        'name': name,
                        'preferred_name': row.get('Preferred Name', '').strip(),
                        'gender': row.get('Gender', '').strip() or '',
                        'email': email,
                        'codementor_username': codementor_username,
                        'timezone': row.get('Timezone', '').strip() or 'UTC',
                        'notes': row.get('Notes', '').strip(),
                        'is_active': row.get('Is Active', 'True').strip().lower() in ('true', '1', 'yes', 'y'),
                        'source': row.get('Source', '').strip() or 'csv',
                        'user': request.user if request.user.is_authenticated else None
                    }

                    # Handle platform preference
                    platform_pref = row.get('Platform Preference', '').strip()
                    if platform_pref:
                        contact_data['platform_preference'] = [p.strip() for p in platform_pref.split(',') if p.strip()]

                    if contact:
                        # Update existing
                        for key, value in contact_data.items():
                            setattr(contact, key, value)
                        contact.save()
                        updated += 1
                    else:
                        # Create new
                        Contact.objects.create(**contact_data)
                        created += 1

                except Exception as e:
                    errors.append(f'Row {row_num}: {str(e)}')

            return Response({
                'message': f'Import completed: {created} created, {updated} updated',
                'created': created,
                'updated': updated,
                'errors': errors
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': f'Failed to import contacts: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='bulk-send')
    def bulk_send(self, request):
        """Send a message to multiple contacts via one or more platforms with rate limiting."""
        contact_ids = request.data.get('contact_ids', [])
        platforms = request.data.get('platforms', [])
        subject = request.data.get('subject', '').strip()
        body = request.data.get('body', '').strip()
        use_preferred_platforms = request.data.get('use_preferred_platforms', False)

        if not contact_ids or not isinstance(contact_ids, list):
            return Response(
                {'error': 'contact_ids must be a non-empty list'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not platforms or not isinstance(platforms, list):
            return Response(
                {'error': 'At least one platform must be specified'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not body:
            return Response(
                {'error': 'Message body is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get contacts
        try:
            contacts = Contact.objects.filter(id__in=contact_ids)
            if contacts.count() != len(contact_ids):
                return Response(
                    {'error': 'Some contacts were not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        except Exception as e:
            return Response(
                {'error': f'Error fetching contacts: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Process in background thread
        def process_bulk_send():
            logger = logging.getLogger('followupper')
            user_settings = UserSettings.get_settings()
            max_concurrent = user_settings.codementor_max_concurrent or 1
            send_interval = user_settings.codementor_send_interval or 5

            # Get credentials once
            gmail_creds = PlatformCredentials.objects.filter(platform='gmail').first()
            codementor_creds = PlatformCredentials.objects.filter(platform='codementor').first()

            gmail_client = None
            if gmail_creds:
                gmail_data = gmail_creds.get_credentials()
                gmail_email = gmail_data.get('email', '').strip()
                app_password = gmail_data.get('app_password', '').strip()
                gmail_name = gmail_data.get('name', '').strip()
                if gmail_email and app_password:
                    client_kwargs = {'email': gmail_email, 'app_password': app_password}
                    if gmail_name:
                        client_kwargs['name'] = gmail_name
                    gmail_client = Client(**client_kwargs)

            codementor_client = None
            if codementor_creds:
                creds_data = codementor_creds.get_credentials()
                access_token = creds_data.get('access_token', '').strip()
                refresh_token = creds_data.get('refresh_token', '').strip()
                if access_token and refresh_token:
                    codementor_client = codementorapi.Client(
                        access_token=access_token,
                        refresh_token=refresh_token
                    )

            # Separate contacts by platform
            email_contacts = []
            codementor_contacts = []

            for contact in contacts:
                contact_platforms = []
                if use_preferred_platforms:
                    preferred = contact.platform_preference or []
                    if 'email' in preferred and contact.email:
                        contact_platforms.append('email')
                    if 'codementor' in preferred and contact.codementor_username:
                        contact_platforms.append('codementor')
                else:
                    if 'email' in platforms and contact.email:
                        contact_platforms.append('email')
                    if 'codementor' in platforms and contact.codementor_username:
                        contact_platforms.append('codementor')

                if 'email' in contact_platforms:
                    email_contacts.append(contact)
                if 'codementor' in contact_platforms:
                    codementor_contacts.append(contact)

            # Helper function to replace template variables
            def replace_template_variables(text, contact_obj):
                """Replace template variables in message text."""
                result = text

                # Get contact data
                first_name = contact_obj.first_name or ''
                preferred_name = contact_obj.preferred_name or ''
                gender = contact_obj.gender or ''

                # Handle gender-based conditionals first
                if gender == 'male':
                    result = re.sub(r'\{if_male:([^}]+)\}', r'\1', result)
                    result = re.sub(r'\{if_female:([^}]+)\}', '', result)
                elif gender == 'female':
                    result = re.sub(r'\{if_female:([^}]+)\}', r'\1', result)
                    result = re.sub(r'\{if_male:([^}]+)\}', '', result)
                else:
                    result = re.sub(r'\{if_male:([^}]+)\}', '', result)
                    result = re.sub(r'\{if_female:([^}]+)\}', '', result)

                # Replace simplified syntax
                result = result.replace('{name}', contact_obj.name or '')
                result = result.replace('{first_name}', first_name)
                result = result.replace('{preferred_name}', preferred_name)
                result = result.replace('{gender}', gender)
                result = result.replace('{email}', contact_obj.email or '')
                result = result.replace('{codementor_username}', contact_obj.codementor_username or '')
                result = result.replace('{notes}', contact_obj.notes or '')

                # Replace old syntax for backwards compatibility
                result = result.replace('{contact.name}', contact_obj.name or '')
                result = result.replace('{contact.first_name}', first_name)
                result = result.replace('{contact.preferred_name}', preferred_name)
                result = result.replace('{contact.gender}', gender)
                result = result.replace('{contact.email}', contact_obj.email or '')
                result = result.replace('{contact.codementor_username}', contact_obj.codementor_username or '')
                result = result.replace('{contact.notes}', contact_obj.notes or '')

                return result

            # Send emails immediately (no rate limiting)
            for contact in email_contacts:
                try:
                    if gmail_client:
                        # Replace template variables per contact
                        email_subject = replace_template_variables(subject, contact) if subject else 'No Subject'
                        email_body = replace_template_variables(body, contact)

                        gmail_client.send_email(to=contact.email, subject=email_subject, body=email_body)

                        # Save message history
                        Message.objects.create(
                            contact=contact,
                            subject=email_subject,
                            body=email_body,
                            platforms=['email'],
                            status='sent',
                            sent_at=timezone.now()
                        )
                        contact.last_messaged = timezone.now()
                        contact.save(update_fields=['last_messaged'])
                except Exception as e:
                    logger.error(f"Failed to send email to {contact.name}: {str(e)}")

            # Send Codementor messages in batches with rate limiting
            rate_limiter = CodementorRateLimiter.get_instance()

            for i in range(0, len(codementor_contacts), max_concurrent):
                batch = codementor_contacts[i:i + max_concurrent]

                # Send batch concurrently
                def send_to_contact(contact):
                    try:
                        logger.info(f"[BULK_SEND] Codementor send requested for contact {contact.id} ({contact.name})")
                        rate_limiter.wait_for_slot(max_concurrent, send_interval)
                        logger.info(f"[BULK_SEND] Rate limit slot acquired for contact {contact.id}")

                        try:
                            if codementor_client:
                                # Replace template variables per contact
                                codementor_body = replace_template_variables(body, contact)

                                send_start = datetime.now()
                                codementor_client.send_message(contact.codementor_username, codementor_body)
                                send_end = datetime.now()
                                logger.info(f"[BULK_SEND] Codementor message sent to {contact.name} in {(send_end - send_start).total_seconds():.2f}s")

                                # Save message history
                                Message.objects.create(
                                    contact=contact,
                                    subject='',
                                    body=codementor_body,
                                    platforms=['codementor'],
                                    status='sent',
                                    sent_at=timezone.now()
                                )
                                contact.last_messaged = timezone.now()
                                contact.save(update_fields=['last_messaged'])
                        finally:
                            rate_limiter.release_slot()
                            logger.info(f"[BULK_SEND] Rate limit slot released for contact {contact.id}")
                    except Exception as e:
                        logger.error(f"[BULK_SEND] Failed to send to {contact.name}: {str(e)}", exc_info=True)
                        try:
                            rate_limiter.release_slot()
                        except BaseException:
                            pass

                # Send batch concurrently using threads
                threads = []
                for contact in batch:
                    thread = threading.Thread(target=send_to_contact, args=(contact,))
                    thread.start()
                    threads.append(thread)

                # Wait for batch to complete
                for thread in threads:
                    thread.join()

                # Wait for interval before next batch (except last batch)
                if i + max_concurrent < len(codementor_contacts):
                    logger.info(f"[BULK_SEND] Waiting {send_interval}s before next batch...")
                    time.sleep(send_interval)

            logger.info(f"[BULK_SEND] Bulk send completed: {len(email_contacts)} emails, {len(codementor_contacts)} Codementor messages")

        # Start background thread
        thread = threading.Thread(target=process_bulk_send)
        thread.daemon = True
        thread.start()

        return Response({
            'message': f'Bulk send initiated for {len(contact_ids)} contact(s). Processing in background.',
            'contact_count': len(contact_ids)
        }, status=status.HTTP_202_ACCEPTED)


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
                'footer': user_settings.footer or '',
                'codementor_max_concurrent': user_settings.codementor_max_concurrent if user_settings.codementor_max_concurrent is not None else 1,
                'codementor_send_interval': user_settings.codementor_send_interval if user_settings.codementor_send_interval is not None else 5
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
            try:
                restart_scheduler()
            except Exception as e:
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
        access_token = request.data.get('access_token', '').strip()
        refresh_token = request.data.get('refresh_token', '').strip()

        if not access_token or not refresh_token:
            return Response(
                {'error': 'Access token and refresh token are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Create client to test connection
            client = codementorapi.Client(
                access_token=access_token,
                refresh_token=refresh_token
            )
            # Try to get sessions to verify credentials work
            client.get_sessions()
            return Response({'message': 'Codementor connection test successful'})
        except Exception as e:
            error_message = str(e)
            if 'authentication' in error_message.lower() or 'token' in error_message.lower():
                return Response(
                    {'error': 'Authentication failed. Please check your access token and refresh token.'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            return Response(
                {'error': f'Connection failed: {error_message}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], url_path='import/codementor')
    @csrf_exempt
    def import_codementor_contacts(self, request):
        """Import contacts from Codementor sessions."""
        # Get Codementor credentials
        codementor_creds = PlatformCredentials.objects.filter(platform='codementor').first()
        if not codementor_creds:
            return Response(
                {'error': 'Codementor credentials not configured'},
                status=status.HTTP_400_BAD_REQUEST
            )

        creds_data = codementor_creds.get_credentials()
        access_token = creds_data.get('access_token', '').strip()
        refresh_token = creds_data.get('refresh_token', '').strip()

        if not access_token or not refresh_token:
            return Response(
                {'error': 'Codementor credentials are incomplete'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Create Codementor client
            client = codementorapi.Client(
                access_token=access_token,
                refresh_token=refresh_token
            )

            # Get all sessions
            sessions = client.get_sessions()

            # Track unique contacts by username to avoid duplicates
            contacts_seen = {}
            created = 0
            updated = 0
            errors = []

            # Process each session to extract mentee information
            for session in sessions:
                try:
                    mentee = session.mentee
                    username = mentee.username

                    # Skip if we've already processed this username
                    if username in contacts_seen:
                        continue

                    # Skip if name is "Removed User"
                    mentee_name = mentee.name or ''
                    if mentee_name.strip() == 'Removed User':
                        continue

                    # Get full session details for more info (optional, but provides timezone)
                    try:
                        session_detail = client.get_session_details(session.id)
                        mentee_detail = session_detail.mentee
                        timezone_region = mentee_detail.time_zone_region or 'UTC'
                    except Exception:
                        # If we can't get details, use basic info
                        timezone_region = 'UTC'

                    # Check if contact already exists (filter by user if authenticated)
                    contact = None
                    if username:
                        if request.user.is_authenticated:
                            contact = Contact.objects.filter(
                                codementor_username=username,
                                user=request.user
                            ).first()
                        else:
                            contact = Contact.objects.filter(
                                codementor_username=username,
                                user__isnull=True
                            ).first()

                    # Prepare contact data
                    # Note: We intentionally do NOT set preferred_name from Codementor
                    contact_data = {
                        'codementor_username': username,
                        'timezone': timezone_region,
                        'platform_preference': ['codementor'],
                        'source': 'Codementor',
                        'user': request.user if request.user.is_authenticated else None
                    }

                    if contact:
                        # Update existing contact - but don't update name if it already exists
                        # Only set name if contact doesn't have one or if it's empty
                        # Also, do NOT update preferred_name from Codementor
                        if not contact.name or contact.name.strip() == '':
                            contact_data['name'] = mentee_name or username or 'Unknown'

                        for key, value in contact_data.items():
                            if key != 'user' or value is not None:
                                setattr(contact, key, value)
                        contact.save()
                        updated += 1
                    else:
                        # Create new contact
                        # Note: preferred_name is intentionally left blank (not set from Codementor)
                        contact_data['name'] = mentee_name or username or 'Unknown'
                        Contact.objects.create(**contact_data)
                        created += 1

                    contacts_seen[username] = True

                except Exception as e:
                    errors.append(f'Error processing session {session.id}: {str(e)}')

            return Response({
                'message': f'Import completed: {created} created, {updated} updated',
                'created': created,
                'updated': updated,
                'errors': errors
            }, status=status.HTTP_200_OK)

        except Exception as e:
            error_message = str(e)
            if 'authentication' in error_message.lower() or 'token' in error_message.lower():
                return Response(
                    {'error': 'Authentication failed. Please check your Codementor credentials.'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            return Response(
                {'error': f'Import failed: {error_message}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], url_path='send-message')
    def send_message(self, request):
        """Send a message to a contact via one or more platforms."""
        # Get contact ID and message data
        contact_id = request.data.get('contact_id')
        platforms = request.data.get('platforms', [])  # List of platforms: ['email', 'codementor']
        subject = request.data.get('subject', '').strip()
        body = request.data.get('body', '').strip()

        if not contact_id:
            return Response(
                {'error': 'Contact ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not platforms or not isinstance(platforms, list):
            return Response(
                {'error': 'At least one platform must be specified'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not body:
            return Response(
                {'error': 'Message body is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get contact
        try:
            contact = Contact.objects.get(id=contact_id)
        except Contact.DoesNotExist:
            return Response(
                {'error': 'Contact not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Validate platforms and get recipients
        valid_platforms = []
        if 'email' in platforms:
            if not contact.email:
                return Response(
                    {'error': 'Contact does not have an email address'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            valid_platforms.append('email')

        if 'codementor' in platforms:
            if not contact.codementor_username:
                return Response(
                    {'error': 'Contact does not have a Codementor username'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            valid_platforms.append('codementor')

        if not valid_platforms:
            return Response(
                {'error': 'No valid platforms available for this contact'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate subject for email
        if 'email' in valid_platforms and not subject:
            return Response(
                {'error': 'Subject is required for email messages'},
                status=status.HTTP_400_BAD_REQUEST
            )

        sent_platforms = []
        errors = []
        email_message_id = None

        # Send via email if requested
        if 'email' in valid_platforms:
            success, msg_id, error = _send_email_message(contact, subject, body)
            if success:
                sent_platforms.append('email')
                email_message_id = msg_id
            else:
                errors.append(error)

        # Send via Codementor if requested (with rate limiting)
        if 'codementor' in valid_platforms:
            success, error = _send_codementor_message(contact, body)
            if success:
                sent_platforms.append('codementor')
            else:
                errors.append(error)

        if not sent_platforms:
            return Response(
                {'error': 'Failed to send message', 'details': errors},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Store in message history
        message_record = _save_message_history(contact, subject, body, sent_platforms, email_message_id)

        response_message = f'Message sent via {", ".join(sent_platforms)}'
        if errors:
            response_message += f' (warnings: {"; ".join(errors)})'

        response_data = {
            'message': response_message,
            'sent_platforms': sent_platforms,
            'errors': errors if errors else None
        }

        # Include email_message_id if available (for chain message threading)
        if email_message_id:
            response_data['email_message_id'] = email_message_id
            if message_record:
                response_data['message_id'] = message_record.id

        return Response(response_data)


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


class MessageSequenceViewSet(viewsets.ModelViewSet):
    queryset = MessageSequence.objects.all()
    serializer_class = MessageSequenceSerializer

    def get_queryset(self):
        """Filter sequences by contact if contact_id is provided."""
        queryset = MessageSequence.objects.all()
        contact_id = self.request.query_params.get('contact_id', None)
        if contact_id:
            queryset = queryset.filter(contact_id=contact_id)
        return queryset.select_related('contact').prefetch_related('messages')


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def get_queryset(self):
        """Filter messages by contact, status, or sequence."""
        queryset = Message.objects.all()
        contact_id = self.request.query_params.get('contact_id', None)
        status_filter = self.request.query_params.get('status', None)
        sequence_id = self.request.query_params.get('sequence_id', None)

        if contact_id:
            queryset = queryset.filter(contact_id=contact_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if sequence_id:
            queryset = queryset.filter(sequence_id=sequence_id)

        return queryset.select_related('contact', 'sequence', 'campaign', 'campaign_assignment').order_by('-created_at')

    @action(detail=True, methods=['post'], url_path='send-now')
    def send_now(self, request, pk=None):
        """Send a pending message immediately."""

        message = self.get_object()

        if message.status != 'pending':
            return Response(
                {'error': 'Message is not pending and cannot be sent'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            scheduler = get_scheduler()
            scheduler.send_scheduled_message(message.contact, message)

            # Refresh message from DB to get updated email_message_id
            message.refresh_from_db()

            return Response({
                'message': 'Message sent successfully',
                'email_message_id': message.email_message_id,
                'status': message.status
            })
        except Exception as e:
            logger = logging.getLogger('followupper')
            logger.error(f"Failed to send message {message.id}: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Failed to send message: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['GET'])
@permission_classes([AllowAny])
@csrf_exempt
def health_check(request):
    """Health check endpoint."""
    return Response({'status': 'healthy', 'message': 'Followupper API is running'})


class InterestSubmissionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing interest submissions (superuser only)."""
    queryset = InterestSubmission.objects.all()
    serializer_class = InterestSubmissionSerializer

    def get_queryset(self):
        """Only superusers can access interest submissions."""
        if self.request.user.is_superuser:
            return InterestSubmission.objects.all()
        return InterestSubmission.objects.none()

    def get_permissions(self):
        """Anyone can submit interest, but only superusers can view/manage."""
        if self.action == 'create':
            return [AllowAny()]
        # But only superusers can view/manage
        return [IsAdminUser()]
