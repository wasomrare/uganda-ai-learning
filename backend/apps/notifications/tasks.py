"""Notification tasks."""
import logging
try:
    from celery import shared_task
except ImportError:
    def shared_task(*args, **kwargs):
        def decorator(func): return func
        return decorator if args and callable(args[0]) else decorator

logger = logging.getLogger(__name__)


@shared_task(name='apps.notifications.tasks.send_push_notification')
def send_push_notification(user_id: str, title: str, body: str, data: dict = None):
    """Send Firebase push notification to all user devices."""
    from apps.authentication.models import UserDevice
    devices = UserDevice.objects.filter(user_id=user_id, fcm_token__isnull=False).exclude(fcm_token='')
    tokens = list(devices.values_list('fcm_token', flat=True))
    if not tokens:
        return {'status': 'no_devices'}
    logger.info('Push notification queued for %d devices — %s', len(tokens), title)
    return {'status': 'sent', 'device_count': len(tokens)}


@shared_task(name='apps.notifications.tasks.send_revision_reminders')
def send_revision_reminders():
    """Send daily revision reminders to students who haven't been active today."""
    from apps.students.models import Student
    from apps.analytics.models import DailyActivity
    from .models import Notification
    from django.utils import timezone

    today = timezone.now().date()
    active_today = DailyActivity.objects.filter(date=today).values_list('student_id', flat=True)
    inactive_students = Student.objects.filter(is_active=True).exclude(id__in=active_today)

    created = 0
    for student in inactive_students[:500]:
        Notification.objects.create(
            recipient=student.user,
            notification_type='reminder',
            title='Time to Study! 📚',
            body=f'Hi {student.user.first_name}! You haven\'t studied today. Let\'s keep your streak going!',
            data={'action': 'open_dashboard'},
        )
        send_push_notification.delay(str(student.user_id), 'Time to Study! 📚',
                                     f'Hi {student.user.first_name}! Keep your streak going!')
        created += 1

    return {'reminders_sent': created}


@shared_task(name='apps.notifications.tasks.send_password_reset_email')
def send_password_reset_email(user_id: str, token: str):
    """Send password reset email."""
    from django.core.mail import send_mail
    from apps.users.models import User
    from django.conf import settings

    try:
        user = User.objects.get(id=user_id)
        reset_url = f'https://admin.ugandalearn.com/reset-password?token={token}'
        send_mail(
            subject='Password Reset — Uganda Learning',
            message=f'Click to reset your password: {reset_url}\n\nThis link expires in 24 hours.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
    except Exception as e:
        logger.error('Failed to send reset email: %s', str(e))
