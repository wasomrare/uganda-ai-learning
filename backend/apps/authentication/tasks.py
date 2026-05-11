"""Authentication background tasks."""
try:
    try:
    from celery import shared_task
except ImportError:
    def shared_task(*args, **kwargs):
        def decorator(func): return func
        return decorator if args and callable(args[0]) else decorator
except ImportError:
    def shared_task(*args, **kwargs):
        def decorator(func): return func
        return decorator if args and callable(args[0]) else decorator
from django.utils import timezone


@shared_task(name='apps.authentication.tasks.cleanup_expired_tokens')
def cleanup_expired_tokens():
    """Remove expired password reset tokens and old login history."""
    from .models import PasswordResetToken, LoginHistory

    cutoff = timezone.now() - timezone.timedelta(days=30)
    deleted_tokens, _ = PasswordResetToken.objects.filter(expires_at__lt=timezone.now()).delete()
    deleted_history, _ = LoginHistory.objects.filter(timestamp__lt=cutoff).delete()

    return {
        'expired_tokens_deleted': deleted_tokens,
        'old_history_deleted': deleted_history,
    }
