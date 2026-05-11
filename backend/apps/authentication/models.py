"""Authentication-related models: devices, sessions, login history, password reset."""
import uuid
from django.db import models
from django.utils import timezone


class UserDevice(models.Model):
    """Tracks registered devices per user."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='devices')
    device_id = models.CharField(max_length=255, db_index=True)
    device_name = models.CharField(max_length=255, blank=True)
    device_type = models.CharField(
        max_length=20,
        choices=[('android', 'Android'), ('ios', 'iOS'), ('web', 'Web'), ('other', 'Other')],
        default='other',
    )
    app_version = models.CharField(max_length=50, blank=True)
    os_version = models.CharField(max_length=50, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    fcm_token = models.TextField(blank=True)
    is_trusted = models.BooleanField(default=False)
    last_seen = models.DateTimeField(auto_now=True)
    first_seen = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'auth_user_devices'
        unique_together = ('user', 'device_id')
        ordering = ['-last_seen']

    def __str__(self):
        return f'{self.user.username} — {self.device_name or self.device_id[:20]}'


class LoginHistory(models.Model):
    """Records every login attempt (success or failure)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        'users.User', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='login_history',
    )
    username_attempted = models.CharField(max_length=150, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    device_id = models.CharField(max_length=255, blank=True)
    success = models.BooleanField(default=False)
    failure_reason = models.CharField(max_length=100, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'auth_login_history'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'success']),
            models.Index(fields=['ip_address', 'timestamp']),
        ]


class PasswordResetToken(models.Model):
    """Secure password reset tokens."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='reset_tokens')
    token = models.CharField(max_length=128, unique=True, db_index=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'auth_password_reset_tokens'

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def is_valid(self):
        return not self.is_used and not self.is_expired


class TokenBlacklist(models.Model):
    """Blacklisted JTI values (in addition to SimpleJWT's built-in blacklist)."""
    jti = models.CharField(max_length=255, unique=True, db_index=True)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='blacklisted_tokens')
    blacklisted_at = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'auth_token_blacklist'
        ordering = ['-blacklisted_at']
