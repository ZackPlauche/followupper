"""
Associate existing contacts with a user.
Usage: python manage.py associate_contacts --username admin
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from followupper.models import Contact


class Command(BaseCommand):
    help = 'Associate existing contacts with a user'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            required=True,
            help='Username to associate contacts with',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Associate ALL contacts (including those already associated with other users)',
        )

    def handle(self, *args, **options):
        username = options['username']
        associate_all = options['all']
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User "{username}" not found'))
            return
        
        # Get contacts to associate
        if associate_all:
            contacts = Contact.objects.all()
            self.stdout.write(self.style.WARNING(f'Associating ALL contacts with user "{username}"'))
        else:
            contacts = Contact.objects.filter(user__isnull=True)
            self.stdout.write(f'Associating unassociated contacts with user "{username}"')
        
        count = contacts.count()
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No contacts to associate'))
            return
        
        # Confirm
        self.stdout.write(f'Found {count} contact(s) to associate')
        if not associate_all:
            self.stdout.write(self.style.SUCCESS(f'This will associate {count} contact(s) with user "{username}"'))
        else:
            self.stdout.write(self.style.WARNING(f'This will associate ALL {count} contact(s) with user "{username}"'))
        
        # Associate contacts
        updated = contacts.update(user=user)
        
        self.stdout.write(self.style.SUCCESS(f'\n[OK] Successfully associated {updated} contact(s) with user "{username}"'))
        self.stdout.write(self.style.SUCCESS('=' * 50))

