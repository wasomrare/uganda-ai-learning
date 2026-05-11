"""Recommendation generation tasks."""
try:
    from celery import shared_task
except ImportError:
    def shared_task(*args, **kwargs):
        def decorator(func): return func
        return decorator if args and callable(args[0]) else decorator
import logging

logger = logging.getLogger(__name__)


@shared_task(name='apps.recommendations.tasks.detect_struggling_learners')
def detect_struggling_learners():
    """Identify students below 50% and generate recommendations."""
    from apps.students.models import Student
    from apps.assessments.models import AssessmentAttempt
    from .models import LearningRecommendation
    from apps.ai_engine.service import ai_service
    from django.db.models import Avg
    from django.utils import timezone

    students = Student.objects.filter(is_active=True)
    generated = 0

    for student in students:
        recent_attempts = AssessmentAttempt.objects.filter(
            student=student,
            status__in=['ai_marked', 'teacher_reviewed'],
        ).order_by('-created_at')[:10]

        if not recent_attempts.exists():
            continue

        avg_score = recent_attempts.aggregate(avg=Avg('percentage'))['avg'] or 0
        if avg_score >= 60:
            continue

        ai_profile = getattr(student, 'ai_profile', None)
        profile_data = {}
        if ai_profile:
            class_level = student.current_class.level if student.current_class else 'P4'
            profile_data = {
                'class_level': class_level,
                'weak_subjects': ai_profile.weak_subjects,
                'weak_topics': ai_profile.weak_topics,
                'accuracy_rate': ai_profile.accuracy_rate,
                'current_streak': ai_profile.current_streak,
            }

        recent_scores = list(recent_attempts.values('percentage', 'assessment__subject__name'))
        recommendations = ai_service.generate_recommendations_sync(profile_data, recent_scores)

        LearningRecommendation.objects.filter(student=student, is_completed=False, ai_generated=True).delete()

        for rec in recommendations:
            if not rec.get('message'):
                continue
            LearningRecommendation.objects.create(
                student=student,
                recommendation_type=rec.get('type', 'revision'),
                message=rec.get('message', ''),
                priority=rec.get('priority', 'medium'),
                estimated_time_minutes=rec.get('estimated_time_minutes', 15),
                ai_generated=True,
                expires_at=timezone.now() + timezone.timedelta(days=7),
            )
            generated += 1

    logger.info('Generated %d recommendations for struggling learners.', generated)
    return {'recommendations_generated': generated}
