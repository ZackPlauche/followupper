"""
Create a default superuser for singleton app.
Usage: python manage.py createsuperuser
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from followupper.models import UserProfile


class Command(BaseCommand):
    help = 'Create or update the default superuser account'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            default='admin@followupper.com',
            help='Email for the superuser (default: admin@followupper.com)',
        )
        parser.add_argument(
            '--password',
            type=str,
            default='admin',
            help='Password for the superuser (default: admin)',
        )
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Username for the superuser (default: admin)',
        )

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        username = options['username']

        # Check if user already exists by username
        try:
            user = User.objects.get(username=username)
            # Update existing user
            user.email = email
            user.is_staff = True
            user.is_superuser = True
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'[OK] Updated existing user: {username}'))
        except User.DoesNotExist:
            # Create new user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_staff=True,
                is_superuser=True
            )
            self.stdout.write(self.style.SUCCESS(f'[OK] Created new superuser: {username}'))

        # Create or update profile
        profile, _ = UserProfile.objects.get_or_create(user=user)
        self.stdout.write(self.style.SUCCESS(f'[OK] User profile ready'))

        self.stdout.write(self.style.SUCCESS('\n' + '=' * 50))
        self.stdout.write(self.style.SUCCESS('Default Login Credentials:'))
        self.stdout.write(self.style.SUCCESS(f'  Username/Email: {email}'))
        self.stdout.write(self.style.SUCCESS(f'  Password: {password}'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
