"""AI Engine Celery tasks — automated question generation, marking, recommendations."""
import logging
try:
    from celery import shared_task
except ImportError:
    def shared_task(*args, **kwargs):
        def decorator(func): return func
        return decorator if args and callable(args[0]) else decorator

logger = logging.getLogger(__name__)


@shared_task(name='apps.ai_engine.tasks.generate_daily_revision_batch', bind=True, max_retries=3)
def generate_daily_revision_batch(self):
    """Auto-generate daily revision questions for all active class levels and subjects."""
    from apps.curriculum.models import Topic
    from apps.subjects.models import Subject
    from apps.question_bank.models import Question
    from .service import ai_service
    from django.utils import timezone
    from django.conf import settings

    today = timezone.now().date()
    class_levels = settings.PRIMARY_CLASSES
    generated_count = 0

    for class_level in class_levels:
        topics = Topic.objects.filter(
            class_level=class_level,
            is_active=True,
        ).select_related('subject').order_by('?')[:3]

        for topic in topics:
            existing_today = Question.objects.filter(
                topic=topic,
                source='ai_generated',
                created_at__date=today,
            ).count()
            if existing_today >= 5:
                continue

            questions_data = ai_service.generate_questions_sync(
                class_level=class_level,
                subject_name=topic.subject.name,
                topic_name=topic.name,
                question_type='mcq',
                difficulty='medium',
                count=5,
                term=1,
            )

            for q_data in questions_data:
                if not q_data.get('question_text'):
                    continue
                try:
                    from apps.question_bank.models import MCQOption, QuestionAnswer
                    question = Question.objects.create(
                        question_type='mcq',
                        subject=topic.subject,
                        topic=topic,
                        class_level=class_level,
                        question_text=q_data.get('question_text', ''),
                        marks=q_data.get('marks', 1),
                        difficulty=q_data.get('difficulty', 'medium'),
                        estimated_time_seconds=q_data.get('estimated_time_seconds', 60),
                        source='ai_generated',
                        is_approved=False,
                        ai_model_used=ai_service.ollama.get_model_name(),
                        learning_objectives=[q_data.get('learning_objective', '')],
                    )

                    for opt in q_data.get('options', []):
                        MCQOption.objects.create(
                            question=question,
                            option_label=opt.get('label', 'A'),
                            option_text=opt.get('text', ''),
                            is_correct=opt.get('is_correct', False),
                            order=['A', 'B', 'C', 'D'].index(opt.get('label', 'A')),
                        )

                    answer_data = q_data.get('answer', {})
                    if answer_data:
                        QuestionAnswer.objects.create(
                            question=question,
                            answer_text=answer_data.get('text', ''),
                            answer_keywords=answer_data.get('keywords', []),
                            explanation=answer_data.get('explanation', ''),
                            hints=answer_data.get('hints', []),
                        )

                    generated_count += 1
                except Exception as e:
                    logger.error('Failed to save AI question: %s', str(e))

    logger.info('Daily AI question batch: %d questions generated.', generated_count)
    return {'generated': generated_count, 'date': str(today)}


@shared_task(name='apps.ai_engine.tasks.generate_weekly_assessments')
def generate_weekly_assessments():
    """Generate a weekly assessment for each class and term week."""
    from apps.assessments.models import Assessment
    from apps.classes.models import SchoolClass
    from apps.subjects.models import Subject
    from django.utils import timezone

    classes = SchoolClass.objects.filter(is_active=True)
    assessments_created = 0

    for school_class in classes:
        subjects = Subject.objects.filter(class_levels__contains=[school_class.level], is_active=True)
        for subject in subjects[:3]:
            week_number = timezone.now().isocalendar()[1]
            Assessment.objects.get_or_create(
                title=f'Week {week_number} {subject.name} Quiz — {school_class.name}',
                school_class=school_class,
                subject=subject,
                assessment_type='weekly_quiz',
                defaults={
                    'is_ai_generated': True,
                    'status': 'draft',
                    'duration_minutes': 20,
                    'total_marks': 10,
                    'class_level': school_class.level,
                },
            )
            assessments_created += 1

    return {'assessments_created': assessments_created}


@shared_task(name='apps.ai_engine.tasks.auto_mark_assessment', bind=True, max_retries=2)
def auto_mark_assessment(self, attempt_id: str):
    """Automatically mark an assessment attempt."""
    from apps.assessments.models import AssessmentAttempt, StudentAnswer
    from .service import ai_service

    try:
        attempt = AssessmentAttempt.objects.get(id=attempt_id)
    except AssessmentAttempt.DoesNotExist:
        return

    total_score = 0.0
    answers = StudentAnswer.objects.filter(attempt=attempt).select_related(
        'question', 'question__answer'
    ).prefetch_related('question__options')

    for student_answer in answers:
        question = student_answer.question
        score = 0.0
        ai_feedback = ''

        if question.question_type == 'mcq':
            correct_option = question.options.filter(is_correct=True).first()
            if correct_option and str(student_answer.selected_option_id) == str(correct_option.id):
                score = question.marks
            student_answer.is_correct = score > 0

        elif question.question_type == 'true_false':
            model_answer = getattr(question.answer, 'answer_text', '').lower()
            student_ans = (student_answer.text_answer or '').lower()
            score = question.marks if student_ans == model_answer else 0
            student_answer.is_correct = score > 0

        elif question.question_type in ('short_answer', 'fill_blank'):
            if hasattr(question, 'answer') and question.answer:
                result = ai_service.grade_short_answer_sync(
                    question_text=question.question_text,
                    model_answer=question.answer.answer_text,
                    keywords=question.answer.answer_keywords,
                    student_answer=student_answer.text_answer or '',
                    max_marks=question.marks,
                    class_level=attempt.assessment.class_level,
                )
                score = result.get('score', 0)
                ai_feedback = result.get('feedback', '')
                student_answer.ai_confidence = result.get('confidence', 0)

        elif question.question_type == 'composition':
            if hasattr(question, 'answer') and question.answer:
                result = ai_service.grade_composition_sync(
                    prompt_text=question.question_text,
                    student_response=student_answer.text_answer or '',
                    max_marks=question.marks,
                    class_level=attempt.assessment.class_level,
                    rubric=question.answer.marking_rubric or {},
                )
                score = result.get('score', 0)
                ai_feedback = result.get('feedback', '')

        student_answer.ai_score = score
        student_answer.ai_feedback = ai_feedback
        student_answer.save(update_fields=['ai_score', 'ai_feedback', 'is_correct', 'ai_confidence'])
        total_score += score

    attempt.ai_score = total_score
    attempt.status = 'ai_marked'
    attempt.save(update_fields=['ai_score', 'status'])

    return {'attempt_id': attempt_id, 'score': total_score}
