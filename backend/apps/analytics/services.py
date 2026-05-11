"""Analytics computation services."""
from django.db.models import Avg, Count, Sum, Max, Min, F
from django.utils import timezone
from datetime import timedelta


def get_student_performance_summary(student) -> dict:
    """Compute full performance summary for a student."""
    from apps.assessments.models import AssessmentAttempt
    from .models import SubjectMastery, TopicMastery, DailyActivity

    attempts = AssessmentAttempt.objects.filter(
        student=student,
        status__in=['ai_marked', 'teacher_reviewed', 'published'],
    )

    total_attempts = attempts.count()
    avg_score = attempts.aggregate(avg=Avg('percentage'))['avg'] or 0
    highest = attempts.aggregate(h=Max('percentage'))['h'] or 0

    subject_mastery = SubjectMastery.objects.filter(student=student).select_related('subject')
    topic_mastery = TopicMastery.objects.filter(student=student).select_related('topic__subject')

    weak_subjects = [
        {'subject': sm.subject.name, 'mastery': sm.mastery_score}
        for sm in subject_mastery if sm.mastery_score < 60
    ]
    strong_subjects = [
        {'subject': sm.subject.name, 'mastery': sm.mastery_score}
        for sm in subject_mastery if sm.mastery_score >= 75
    ]

    weak_topics = [
        {'topic': tm.topic.name, 'subject': tm.topic.subject.name, 'mastery': tm.mastery_score}
        for tm in topic_mastery if tm.mastery_score < 50
    ]

    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    activity = DailyActivity.objects.filter(student=student, date__gte=thirty_days_ago)
    total_time = activity.aggregate(t=Sum('time_spent_minutes'))['t'] or 0
    active_days = activity.count()

    ai_profile = getattr(student, 'ai_profile', None)

    return {
        'total_attempts': total_attempts,
        'average_score': round(avg_score, 2),
        'highest_score': round(highest, 2),
        'active_days_last_30': active_days,
        'total_time_spent_hours': round(total_time / 60, 1),
        'current_streak': getattr(ai_profile, 'current_streak', 0),
        'ple_readiness_score': getattr(ai_profile, 'ple_readiness_score', 0),
        'overall_mastery': getattr(ai_profile, 'overall_mastery', 0),
        'weak_subjects': weak_subjects[:5],
        'strong_subjects': strong_subjects[:5],
        'weak_topics': weak_topics[:10],
        'subject_mastery': [
            {
                'subject': sm.subject.name,
                'mastery': sm.mastery_score,
                'accuracy': sm.accuracy,
                'attempts': sm.attempts,
            }
            for sm in subject_mastery
        ],
    }


def update_mastery_after_attempt(attempt) -> None:
    """Recalculate mastery after an assessment attempt is marked."""
    from .models import SubjectMastery, TopicMastery
    from apps.assessments.models import StudentAnswer

    student = attempt.student
    assessment = attempt.assessment

    if not assessment.subject:
        return

    answers = StudentAnswer.objects.filter(attempt=attempt).select_related('question__topic')

    total_questions = answers.count()
    correct_answers = answers.filter(is_correct=True).count()

    if total_questions == 0:
        return

    subject_mastery, _ = SubjectMastery.objects.get_or_create(
        student=student,
        subject=assessment.subject,
        class_level=attempt.assessment.class_level,
    )
    subject_mastery.attempts += total_questions
    subject_mastery.correct += correct_answers
    subject_mastery.last_practiced = timezone.now()
    new_accuracy = (subject_mastery.correct / subject_mastery.attempts) * 100
    subject_mastery.mastery_score = round(
        (subject_mastery.mastery_score * 0.3 + new_accuracy * 0.7), 2
    )
    subject_mastery.save()

    topic_groups = {}
    for ans in answers:
        if ans.question.topic_id:
            tid = ans.question.topic_id
            if tid not in topic_groups:
                topic_groups[tid] = {'topic': ans.question.topic, 'total': 0, 'correct': 0}
            topic_groups[tid]['total'] += 1
            topic_groups[tid]['correct'] += 1 if ans.is_correct else 0

    for topic_id, data in topic_groups.items():
        tm, _ = TopicMastery.objects.get_or_create(student=student, topic_id=topic_id)
        tm.attempts += data['total']
        tm.correct += data['correct']
        tm.last_practiced = timezone.now()
        accuracy = (tm.correct / tm.attempts) * 100
        tm.mastery_score = round((tm.mastery_score * 0.3 + accuracy * 0.7), 2)
        tm.save()

    ai_profile = getattr(student, 'ai_profile', None)
    if ai_profile:
        all_subject_masteries = SubjectMastery.objects.filter(student=student)
        if all_subject_masteries.exists():
            avg_mastery = all_subject_masteries.aggregate(avg=Avg('mastery_score'))['avg'] or 0
            ai_profile.overall_mastery = round(avg_mastery, 2)

        weak_topics = list(
            TopicMastery.objects.filter(student=student, mastery_score__lt=50)
            .select_related('topic')
            .values_list('topic__name', flat=True)[:10]
        )
        strong_topics = list(
            TopicMastery.objects.filter(student=student, mastery_score__gte=80)
            .select_related('topic')
            .values_list('topic__name', flat=True)[:10]
        )
        ai_profile.weak_topics = weak_topics
        ai_profile.strong_topics = strong_topics
        ai_profile.save(update_fields=['overall_mastery', 'weak_topics', 'strong_topics'])
