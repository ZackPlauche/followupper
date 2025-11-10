"""
Authentication views for Followupper.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import UserProfile, PlatformCredentials
import qrcode
import io
import base64
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Register a new user."""
    email = request.data.get('email')
    password = request.data.get('password')
    username = request.data.get('username', email)

    if not email or not password:
        return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email=email).exists():
        return Response({'error': 'Email already registered'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already taken'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        # Create user profile
        UserProfile.objects.create(user=user)
        
        # Auto-login after registration
        login(request, user)
        
        return Response({
            'message': 'User created successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Login a user."""
    email = request.data.get('email')
    password = request.data.get('password')
    two_factor_token = request.data.get('two_factor_token')

    if not email or not password:
        return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

    # Try to find user by email
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    # Authenticate user
    user = authenticate(request, username=user.username, password=password)
    if not user:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    # Check if 2FA is enabled
    profile, _ = UserProfile.objects.get_or_create(user=user)
    if profile.two_factor_enabled:
        if not two_factor_token:
            return Response({
                'requires_2fa': True,
                'message': 'Two-factor authentication required'
            }, status=status.HTTP_200_OK)
        
        if not profile.verify_2fa_token(two_factor_token):
            return Response({'error': 'Invalid 2FA token'}, status=status.HTTP_401_UNAUTHORIZED)

    # Login user
    login(request, user)
    
    return Response({
        'message': 'Login successful',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])  # Allow logout even if not authenticated (idempotent)
def logout_view(request):
    """Logout a user (idempotent - works even if already logged out)."""
    # Only logout if user is authenticated
    if request.user.is_authenticated:
        logout(request)
    
    # Always clear session data
    request.session.flush()
    
    # Create response
    response = Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
    
    # Clear cookies with proper settings
    response.delete_cookie('sessionid', path='/', samesite='Lax')
    response.delete_cookie('csrftoken', path='/', samesite='Lax')
    
    # Also try to clear with domain if set
    from django.conf import settings
    if hasattr(settings, 'SESSION_COOKIE_DOMAIN') and settings.SESSION_COOKIE_DOMAIN:
        response.delete_cookie('sessionid', domain=settings.SESSION_COOKIE_DOMAIN, path='/')
        response.delete_cookie('csrftoken', domain=settings.SESSION_COOKIE_DOMAIN, path='/')
    
    return response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Change user's password."""
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    
    if not old_password or not new_password:
        return Response({'error': 'Old password and new password are required'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = request.user
    
    # Verify old password
    if not user.check_password(old_password):
        return Response({'error': 'Current password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Set new password
    user.set_password(new_password)
    user.save()
    
    return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])  # Allow unauthenticated requests to check auth status
def current_user(request):
    """Get current authenticated user."""
    from django.middleware.csrf import get_token
    
    # Check if user is authenticated
    if not request.user.is_authenticated:
        return Response({'error': 'Not authenticated'}, status=status.HTTP_403_FORBIDDEN)
    
    # Ensure CSRF token is set in cookies
    get_token(request)
    
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)
    
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'two_factor_enabled': profile.two_factor_enabled,
        'is_superuser': user.is_superuser
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset(request):
    """Request a password reset email."""
    email = request.data.get('email')
    
    if not email:
        return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
        profile, _ = UserProfile.objects.get_or_create(user=user)
        token = profile.generate_password_reset_token()
        
        # Get Gmail credentials from PlatformCredentials
        gmail_creds = PlatformCredentials.objects.filter(platform='gmail').first()
        if not gmail_creds:
            return Response({'error': 'Email service not configured'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        gmail_data = gmail_creds.get_credentials()
        gmail_email = gmail_data.get('email')
        gmail_password = gmail_data.get('app_password')
        
        if not gmail_email or not gmail_password:
            return Response({'error': 'Email service not configured'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Send password reset email using Gmail SMTP
        reset_url = f"{request.scheme}://{request.get_host()}/reset-password?token={token}"
        
        try:
            msg = MIMEMultipart()
            msg['From'] = gmail_email
            msg['To'] = email
            msg['Subject'] = 'Password Reset Request - Followupper'
            
            body = f'''Click the following link to reset your password:
            
{reset_url}

This link will expire in 1 hour.

If you did not request this password reset, please ignore this email.
'''
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(gmail_email, gmail_password)
            server.send_message(msg)
            server.quit()
            
            return Response({'message': 'Password reset email sent'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f'Failed to send email: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    except User.DoesNotExist:
        # Don't reveal if email exists
        return Response({'message': 'If the email exists, a password reset link has been sent'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    """Reset password using token."""
    token = request.data.get('token')
    new_password = request.data.get('password')
    
    if not token or not new_password:
        return Response({'error': 'Token and password are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        profile = UserProfile.objects.get(password_reset_token=token)
        
        if profile.password_reset_expires and profile.password_reset_expires < timezone.now():
            return Response({'error': 'Password reset token has expired'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Reset password
        user = profile.user
        user.set_password(new_password)
        user.save()
        
        # Clear reset token
        profile.password_reset_token = ''
        profile.password_reset_expires = None
        profile.save()
        
        return Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)
    except UserProfile.DoesNotExist:
        return Response({'error': 'Invalid reset token'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def setup_2fa(request):
    """Setup 2FA for the current user."""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    
    if not profile.two_factor_secret:
        profile.generate_2fa_secret()
    
    qr_url = profile.get_2fa_qr_url()
    
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return Response({
        'secret': profile.two_factor_secret,
        'qr_code': f'data:image/png;base64,{img_str}',
        'qr_url': qr_url
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enable_2fa(request):
    """Enable 2FA after verifying token."""
    token = request.data.get('token')
    
    if not token:
        return Response({'error': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)

    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    
    if not profile.two_factor_secret:
        return Response({'error': '2FA not set up. Please set up 2FA first.'}, status=status.HTTP_400_BAD_REQUEST)
    
    if not profile.verify_2fa_token(token):
        return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
    
    profile.two_factor_enabled = True
    profile.save()
    
    return Response({'message': '2FA enabled successfully'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def disable_2fa(request):
    """Disable 2FA for the current user."""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    profile.two_factor_enabled = False
    profile.two_factor_secret = ''
    profile.save()
    
    return Response({'message': '2FA disabled successfully'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def submit_interest(request):
    """Submit an interest form."""
    from .models import InterestSubmission
    
    name = request.data.get('name', '').strip()
    email = request.data.get('email', '').strip()
    message = request.data.get('message', '').strip()
    
    if not name or not email:
        return Response({'error': 'Name and email are required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        submission = InterestSubmission.objects.create(
            name=name,
            email=email,
            message=message,
            status='pending'
        )
        return Response({
            'message': 'Thank you for your interest! We\'ll be in touch soon.',
            'id': submission.id
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': f'Failed to submit interest: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

