"""Leaderboard computation tasks."""
try:
    from celery import shared_task
except ImportError:
    def shared_task(*args, **kwargs):
        def decorator(func): return func
        return decorator if args and callable(args[0]) else decorator
import logging

logger = logging.getLogger(__name__)


@shared_task(name='apps.leaderboards.tasks.update_all_leaderboards')
def update_all_leaderboards():
    from .models import Leaderboard, LeaderboardEntry
    from apps.students.models import Student
    from apps.gamification.models import StudentXP, Streak
    from apps.assessments.models import AssessmentAttempt
    from django.utils import timezone
    from django.db.models import Avg, Count

    today = timezone.now().date()
    week_start = today - __import__('datetime').timedelta(days=today.weekday())

    students = Student.objects.filter(is_active=True).select_related('current_class')
    if not students.exists():
        return {'status': 'no_students'}

    lb, _ = Leaderboard.objects.get_or_create(
        leaderboard_type='weekly',
        period_start=week_start,
        period_end=week_start + __import__('datetime').timedelta(days=6),
    )
    LeaderboardEntry.objects.filter(leaderboard=lb).delete()

    entries = []
    for student in students:
        xp_obj = StudentXP.objects.filter(student=student).first()
        streak_obj = Streak.objects.filter(student=student).first()
        attempts = AssessmentAttempt.objects.filter(
            student=student,
            created_at__date__gte=week_start,
            status__in=['ai_marked', 'teacher_reviewed', 'published'],
        )
        avg_score = attempts.aggregate(a=Avg('percentage'))['a'] or 0
        entries.append({
            'student': student,
            'score': avg_score,
            'xp': getattr(xp_obj, 'weekly_xp', 0),
            'assessments_completed': attempts.count(),
            'accuracy': avg_score,
            'streak': getattr(streak_obj, 'current_streak', 0),
        })

    entries.sort(key=lambda x: (x['score'], x['xp']), reverse=True)
    for rank, entry in enumerate(entries, start=1):
        LeaderboardEntry.objects.create(leaderboard=lb, rank=rank, **entry)

    return {'updated': len(entries)}
