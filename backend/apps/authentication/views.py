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
    LoginSerializer, LogoutSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    UserDeviceSerializer, LoginHistorySerializer,
)

logger = logging.getLogger(__name__)


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
