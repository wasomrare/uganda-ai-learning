"""Performance calculation tasks."""
try:
    from celery import shared_task
except ImportError:
    def shared_task(*args, **kwargs):
        def decorator(func): return func
        return decorator if args and callable(args[0]) else decorator
import logging

logger = logging.getLogger(__name__)


@shared_task(name='apps.performance.tasks.calculate_mastery_scores')
def calculate_mastery_scores():
    """Recalculate mastery scores for recently marked attempts."""
    from apps.analytics.services import update_mastery_after_attempt
    from apps.assessments.models import AssessmentAttempt
    from django.utils import timezone
    from datetime import timedelta

    cutoff = timezone.now() - timedelta(hours=2)
    attempts = AssessmentAttempt.objects.filter(
        status='ai_marked',
        updated_at__gte=cutoff,
    ).select_related('student', 'assessment__subject')

    processed = 0
    for attempt in attempts:
        try:
            update_mastery_after_attempt(attempt)
            processed += 1
        except Exception as e:
            logger.error('Mastery calc failed for attempt %s: %s', attempt.id, str(e))

    return {'processed': processed}
