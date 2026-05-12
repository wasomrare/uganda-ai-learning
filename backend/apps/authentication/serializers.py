"""Authentication serializers."""
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from apps.users.models import User


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Enriched JWT token with user data."""
    username_field = 'username'

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['full_name'] = user.get_full_name()
        token['username'] = user.username
        token['force_password_change'] = user.force_password_change
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        data['user'] = {
            'id': str(user.id),
            'username': user.username,
            'full_name': user.get_full_name(),
            'email': user.email,
            'role': user.role,
            'avatar': user.avatar.url if user.avatar else None,
            'force_password_change': user.force_password_change,
        }
        return data


class RegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True, max_length=100)
    last_name = serializers.CharField(required=True, max_length=100)
    username = serializers.CharField(required=True, max_length=150)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(required=True, min_length=6, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)
    role = serializers.ChoiceField(choices=['student', 'teacher', 'parent'], default='student')

    def validate_username(self, value):
        from apps.users.models import User
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError('This username is already taken.')
        return value

    def validate_email(self, value):
        if not value:
            return value
        from apps.users.models import User
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('An account with this email already exists.')
        return value

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({'confirm_password': 'Passwords do not match.'})
        return data


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    device_id = serializers.CharField(required=False, allow_blank=True)
    device_name = serializers.CharField(required=False, allow_blank=True)
    fcm_token = serializers.CharField(required=False, allow_blank=True)


class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({'confirm_password': 'Passwords do not match.'})
        return data


class LoginHistorySerializer(serializers.Serializer):
    id = serializers.UUIDField()
    ip_address = serializers.CharField()
    user_agent = serializers.CharField()
    success = serializers.BooleanField()
    failure_reason = serializers.CharField()
    timestamp = serializers.DateTimeField()


class UserDeviceSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    device_id = serializers.CharField()
    device_name = serializers.CharField()
    device_type = serializers.CharField()
    app_version = serializers.CharField()
    is_trusted = serializers.BooleanField()
    last_seen = serializers.DateTimeField()
