"""User serializers."""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['bio', 'date_of_birth', 'gender', 'address', 'district', 'nationality']


class UserListSerializer(serializers.ModelSerializer):
    """Minimal user info for lists."""
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'email', 'role', 'is_active', 'created_at', 'avatar']


class UserDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'phone', 'role',
            'first_name', 'last_name', 'full_name',
            'avatar', 'is_active', 'is_verified',
            'force_password_change', 'last_login', 'last_login_ip',
            'created_at', 'updated_at', 'profile',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_login', 'last_login_ip']


class CreateUserSerializer(serializers.ModelSerializer):
    """Used by super admin to create new accounts."""
    password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)
    profile = UserProfileSerializer(required=False)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'phone', 'role',
            'first_name', 'last_name', 'password', 'confirm_password',
            'is_active', 'profile',
        ]

    def validate(self, data):
        password = data.get('password')
        confirm = data.get('confirm_password')
        if password and confirm and password != confirm:
            raise serializers.ValidationError({'confirm_password': 'Passwords do not match.'})
        if password:
            validate_password(password)
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        profile_data = validated_data.pop('profile', None)
        password = validated_data.pop('password', None)

        from core.utils import generate_secure_password
        if not password:
            password = generate_secure_password()
            validated_data['force_password_change'] = True

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        UserProfile.objects.create(user=user, **(profile_data or {}))
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({'confirm_password': 'Passwords do not match.'})
        return data


class AdminResetPasswordSerializer(serializers.Serializer):
    """Admin resets a user's password."""
    new_password = serializers.CharField(required=False)
    auto_generate = serializers.BooleanField(default=True)
