"""Analytics background tasks."""
try:
    from celery import shared_task
except ImportError:
    def shared_task(*args, **kwargs):
        def decorator(func): return func
        return decorator if args and callable(args[0]) else decorator
import logging

logger = logging.getLogger(__name__)


@shared_task(name='apps.analytics.tasks.process_daily_analytics')
def process_daily_analytics():
    """Compute daily analytics snapshots for all students."""
    from apps.students.models import Student
    from apps.assessments.models import AssessmentAttempt
    from .models import DailyActivity
    from django.utils import timezone

    today = timezone.now().date()
    students = Student.objects.filter(is_active=True).select_related('ai_profile')
    processed = 0

    for student in students:
        attempts_today = AssessmentAttempt.objects.filter(
            student=student,
            created_at__date=today,
        )
        if not attempts_today.exists():
            continue

        from django.db.models import Sum, Count
        stats = attempts_today.aggregate(
            count=Count('id'),
        )

        from apps.assessments.models import StudentAnswer
        answers = StudentAnswer.objects.filter(attempt__in=attempts_today)
        answer_stats = answers.aggregate(
            total=Count('id'),
            correct=Count('id', filter=__import__('django.db.models', fromlist=['Q']).Q(is_correct=True)),
        )

        activity, _ = DailyActivity.objects.update_or_create(
            student=student, date=today,
            defaults={
                'assessments_taken': stats['count'],
                'questions_attempted': answer_stats['total'] or 0,
                'questions_correct': answer_stats['correct'] or 0,
            }
        )
        processed += 1

    logger.info('Daily analytics processed for %d students.', processed)
    return {'processed': processed}
