"""Authentication views — login, logout, token management, login history."""
import secrets
import logging
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from core.utils import get_client_ip, success_response
from apps.users.models import User
from .models import LoginHistory, UserDevice, PasswordResetToken
from .serializers import (
    RegisterSerializer, LoginSerializer, LogoutSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    UserDeviceSerializer, LoginHistorySerializer,
)

logger = logging.getLogger(__name__)


class GoogleLoginView(APIView):
    """Login or auto-register via Google ID token. No email verification required."""
    permission_classes = [AllowAny]

    def post(self, request):
        id_token_str = request.data.get('id_token')
        if not id_token_str:
            return Response({'error': 'id_token is required.'}, status=400)

        google_client_id = getattr(settings, 'GOOGLE_CLIENT_ID', '')
        if not google_client_id:
            return Response({'error': 'Google login is not configured on this server.'}, status=503)

        try:
            from google.oauth2 import id_token as google_id_token
            from google.auth.transport import requests as google_requests
            idinfo = google_id_token.verify_oauth2_token(
                id_token_str,
                google_requests.Request(),
                google_client_id,
            )
        except ValueError:
            return Response({'error': 'Invalid or expired Google token.'}, status=400)

        email = idinfo.get('email', '')
        first_name = idinfo.get('given_name', '')
        last_name = idinfo.get('family_name', '')

        if not email:
            return Response({'error': 'Google account must have an email address.'}, status=400)

        user = User.objects.filter(email=email).first()
        if not user:
            base = email.split('@')[0]
            username, n = base, 1
            while User.objects.filter(username=username).exists():
                username = f'{base}{n}'
                n += 1
            user = User(
                username=username,
                email=email,
                first_name=first_name or base,
                last_name=last_name or '',
                role='student',
                is_active=True,
                is_verified=True,
                force_password_change=False,
            )
            user.set_unusable_password()
            user.save()
        else:
            changed = []
            if not user.is_verified:
                user.is_verified = True
                changed.append('is_verified')
            if user.force_password_change:
                user.force_password_change = False
                changed.append('force_password_change')
            if changed:
                user.save(update_fields=changed)

        ip = get_client_ip(request)
        ua = request.META.get('HTTP_USER_AGENT', '')
        LoginHistory.objects.create(
            user=user,
            ip_address=ip or None,
            user_agent=ua[:255],
            success=True,
            failure_reason='',
        )

        refresh = RefreshToken.for_user(user)
        return Response(success_response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': str(user.id),
                'username': user.username,
                'full_name': user.get_full_name(),
                'email': user.email,
                'role': user.role,
                'avatar': None,
                'force_password_change': False,
            },
        }, 'Google login successful.'))


class RegisterView(APIView):
    """Self-registration — creates account and returns JWT tokens immediately. No verification required."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = User(
            username=data['username'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data.get('email') or None,
            role=data.get('role', 'student'),
            is_active=True,
            is_verified=True,
            force_password_change=False,
        )
        user.set_password(data['password'])
        user.save()

        ip = get_client_ip(request)
        ua = request.META.get('HTTP_USER_AGENT', '')
        LoginHistory.objects.create(
            user=user,
            ip_address=ip or None,
            user_agent=ua[:255],
            success=True,
            failure_reason='',
        )

        refresh = RefreshToken.for_user(user)
        return Response(success_response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': str(user.id),
                'username': user.username,
                'full_name': user.get_full_name(),
                'email': user.email,
                'role': user.role,
                'avatar': None,
                'force_password_change': False,
            },
        }, 'Account created successfully.'), status=201)


class LoginView(APIView):
    """Login endpoint — returns JWT access + refresh tokens."""
    permission_classes = [AllowAny]
    throttle_scope = 'auth'

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = authenticate(
            request=request,
            username=data['username'],
            password=data['password'],
        )

        ip = get_client_ip(request)
        ua = request.META.get('HTTP_USER_AGENT', '')

        if not user:
            LoginHistory.objects.create(
                username_attempted=data['username'],
                ip_address=ip,
                user_agent=ua[:255],
                success=False,
                failure_reason='invalid_credentials',
            )
            return Response({'error': 'Invalid username or password.'}, status=401)

        if not user.is_active:
            LoginHistory.objects.create(
                user=user, ip_address=ip, user_agent=ua[:255],
                success=False, failure_reason='account_inactive',
            )
            return Response({'error': 'Your account has been deactivated.'}, status=403)

        refresh = RefreshToken.for_user(user)
        refresh['role'] = user.role
        refresh['full_name'] = user.get_full_name()
        refresh['force_password_change'] = user.force_password_change

        user.last_login = timezone.now()
        user.last_login_ip = ip
        user.last_device = ua[:255]
        user.save(update_fields=['last_login', 'last_login_ip', 'last_device'])

        LoginHistory.objects.create(
            user=user, ip_address=ip, user_agent=ua[:255],
            device_id=data.get('device_id', ''),
            success=True,
        )

        if data.get('device_id'):
            UserDevice.objects.update_or_create(
                user=user, device_id=data['device_id'],
                defaults={
                    'device_name': data.get('device_name', ''),
                    'fcm_token': data.get('fcm_token', ''),
                    'user_agent': ua[:255],
                    'ip_address': ip,
                    'last_seen': timezone.now(),
                }
            )

        return Response(success_response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': str(user.id),
                'username': user.username,
                'full_name': user.get_full_name(),
                'email': user.email,
                'role': user.role,
                'avatar': request.build_absolute_uri(user.avatar.url) if user.avatar else None,
                'force_password_change': user.force_password_change,
            },
        }, 'Login successful.'))


class LogoutView(APIView):
    """Blacklist refresh token on logout."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            token = RefreshToken(serializer.validated_data['refresh'])
            token.blacklist()
        except TokenError:
            pass
        return Response(success_response({}, 'Logged out successfully.'))


class TokenRefreshView(APIView):
    """Refresh access token."""
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'error': 'Refresh token required.'}, status=400)
        try:
            refresh = RefreshToken(refresh_token)
            return Response(success_response({
                'access': str(refresh.access_token),
            }, 'Token refreshed.'))
        except TokenError as e:
            return Response({'error': 'Invalid or expired refresh token.'}, status=401)


class PasswordResetRequestView(APIView):
    """Request password reset via email."""
    permission_classes = [AllowAny]
    throttle_scope = 'auth'

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email, is_active=True)
            token_value = secrets.token_urlsafe(48)
            expires = timezone.now() + timezone.timedelta(hours=24)
            PasswordResetToken.objects.create(user=user, token=token_value, expires_at=expires)
            from apps.notifications.tasks import send_password_reset_email
            send_password_reset_email.delay(str(user.id), token_value)
        except User.DoesNotExist:
            pass

        return Response(success_response(
            {},
            'If that email is registered, a reset link has been sent.',
        ))


class PasswordResetConfirmView(APIView):
    """Confirm password reset with token."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            reset_token = PasswordResetToken.objects.select_related('user').get(
                token=data['token'], is_used=False,
            )
        except PasswordResetToken.DoesNotExist:
            return Response({'error': 'Invalid or expired token.'}, status=400)

        if reset_token.is_expired:
            return Response({'error': 'Token has expired.'}, status=400)

        user = reset_token.user
        user.set_password(data['new_password'])
        user.force_password_change = False
        user.save()

        reset_token.is_used = True
        reset_token.used_at = timezone.now()
        reset_token.save()

        return Response(success_response({}, 'Password reset successfully.'))


class LoginHistoryView(APIView):
    """View own login history."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        history = request.user.login_history.all()[:50]
        data = LoginHistorySerializer(history, many=True).data
        return Response(success_response(data))


class MyDevicesView(APIView):
    """View and manage own devices."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        devices = request.user.devices.all()
        data = UserDeviceSerializer(devices, many=True).data
        return Response(success_response(data))

    def delete(self, request, device_id):
        try:
            device = request.user.devices.get(id=device_id)
            device.delete()
            return Response(success_response({}, 'Device removed.'))
        except UserDevice.DoesNotExist:
            return Response({'error': 'Device not found.'}, status=404)
