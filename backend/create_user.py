"""
Direct script to create/update superuser.
This bypasses Django's command system to avoid conflicts.
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from followupper.models import UserProfile

def create_superuser(email='admin@followupper.com', password='admin', username='admin'):
    """Create or update the default superuser account."""
    try:
        user = User.objects.get(username=username)
        # Update existing user
        user.email = email
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()
        print(f'[OK] Updated existing user: {username}')
    except User.DoesNotExist:
        # Create new user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_staff=True,
            is_superuser=True
        )
        print(f'[OK] Created new superuser: {username}')

    # Create or update profile
    profile, _ = UserProfile.objects.get_or_create(user=user)
    print(f'[OK] User profile ready')

    print('\n' + '=' * 50)
    print('Default Login Credentials:')
    print(f'  Username/Email: {email}')
    print(f'  Password: {password}')
    print('=' * 50)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Create or update superuser')
    parser.add_argument('--email', default='admin@followupper.com', help='Email for superuser')
    parser.add_argument('--password', default='admin', help='Password for superuser')
    parser.add_argument('--username', default='admin', help='Username for superuser')
    args = parser.parse_args()
    
    create_superuser(args.email, args.password, args.username)

