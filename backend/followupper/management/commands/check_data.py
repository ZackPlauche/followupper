"""
Check what data exists in the database.
"""
from django.core.management.base import BaseCommand
from followupper.models import Contact, MessageTemplate, Message, Campaign, PlatformCredentials, UserSettings


class Command(BaseCommand):
    help = 'Check what data exists in the database'

    def handle(self, *args, **options):
        contacts_count = Contact.objects.count()
        templates_count = MessageTemplate.objects.count()
        messages_count = Message.objects.count()
        campaigns_count = Campaign.objects.count()
        gmail_creds = PlatformCredentials.objects.filter(platform='gmail').first()
        codementor_creds = PlatformCredentials.objects.filter(platform='codementor').first()
        user_settings = UserSettings.get_settings()

        self.stdout.write(self.style.SUCCESS('\n' + '=' * 50))
        self.stdout.write(self.style.SUCCESS('Database Data Summary:'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(f'Contacts: {contacts_count}')
        self.stdout.write(f'Templates: {templates_count}')
        self.stdout.write(f'Messages: {messages_count}')
        self.stdout.write(f'Campaigns: {campaigns_count}')
        self.stdout.write(f'Gmail Credentials: {"Yes" if gmail_creds else "No"}')
        self.stdout.write(f'Codementor Credentials: {"Yes" if codementor_creds else "No"}')
        self.stdout.write(f'User Settings: Timezone={user_settings.timezone}, Footer={len(user_settings.footer)} chars')
        
        if contacts_count > 0:
            self.stdout.write(self.style.SUCCESS('\nFirst 5 Contacts:'))
            for contact in Contact.objects.all()[:5]:
                self.stdout.write(f'  - {contact.name} ({contact.email})')
        
        if templates_count > 0:
            self.stdout.write(self.style.SUCCESS('\nTemplates:'))
            for template in MessageTemplate.objects.all():
                self.stdout.write(f'  - {template.name}')
        
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 50))

