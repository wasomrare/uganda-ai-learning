"""Offline sync processing tasks."""
try:
    from celery import shared_task
except ImportError:
    def shared_task(*args, **kwargs):
        def decorator(func): return func
        return decorator if args and callable(args[0]) else decorator
import logging

logger = logging.getLogger(__name__)


@shared_task(name='apps.offline_sync.tasks.process_sync_queue')
def process_sync_queue():
    """Process all pending sync queue items."""
    from .models import SyncQueue
    from django.utils import timezone

    pending = SyncQueue.objects.filter(status='pending').select_related('student')[:50]
    processed = failed = 0

    for item in pending:
        item.status = 'processing'
        item.save(update_fields=['status'])
        try:
            _process_sync_item(item)
            item.status = 'synced'
            item.synced_at = timezone.now()
            item.save(update_fields=['status', 'synced_at'])
            processed += 1
        except Exception as e:
            item.retry_count += 1
            item.error_message = str(e)[:500]
            item.status = 'failed' if item.retry_count >= item.max_retries else 'pending'
            item.save(update_fields=['retry_count', 'error_message', 'status'])
            failed += 1
            logger.error('Sync item %s failed: %s', item.id, str(e))

    return {'processed': processed, 'failed': failed}


def _process_sync_item(item):
    """Process a single sync queue item based on entity type."""
    if item.entity_type == 'assessment_attempt':
        pass
    elif item.entity_type == 'daily_activity':
        from apps.analytics.models import DailyActivity
        from django.utils import timezone
        DailyActivity.objects.update_or_create(
            student=item.student,
            date=item.payload.get('date', timezone.now().date()),
            defaults={
                'questions_attempted': item.payload.get('questions_attempted', 0),
                'questions_correct': item.payload.get('questions_correct', 0),
                'time_spent_minutes': item.payload.get('time_spent_minutes', 0),
            }
        )
    elif item.entity_type == 'gamification':
        from apps.gamification.models import award_xp
        award_xp(item.student, item.payload.get('xp', 0), item.payload.get('reason', 'offline_activity'))
