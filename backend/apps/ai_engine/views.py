"""AI Engine API views — generation, chat, marking triggers."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.throttling import ScopedRateThrottle

from core.permissions import IsSuperAdminOrTeacher, IsStudent
from core.utils import success_response
from .service import ai_service
from .tasks import auto_mark_assessment


class GenerateQuestionsView(APIView):
    """Generate AI questions on demand."""
    permission_classes = [IsSuperAdminOrTeacher]
    throttle_scope = 'ai_generation'

    def post(self, request):
        class_level = request.data.get('class_level', 'P4')
        subject_name = request.data.get('subject_name', '')
        topic_name = request.data.get('topic_name', '')
        question_type = request.data.get('question_type', 'mcq')
        difficulty = request.data.get('difficulty', 'medium')
        count = min(int(request.data.get('count', 5)), 20)
        term = int(request.data.get('term', 1))
        save_to_bank = request.data.get('save_to_bank', True)

        if not subject_name or not topic_name:
            return Response({'error': 'subject_name and topic_name are required.'}, status=400)

        questions_data = ai_service.generate_questions_sync(
            class_level=class_level,
            subject_name=subject_name,
            topic_name=topic_name,
            question_type=question_type,
            difficulty=difficulty,
            count=count,
            term=term,
        )

        saved_ids = []
        if save_to_bank and questions_data:
            from apps.question_bank.models import Question, MCQOption, QuestionAnswer
            from apps.subjects.models import Subject

            try:
                subject = Subject.objects.get(name__icontains=subject_name)
                for q_data in questions_data:
                    if not q_data.get('question_text'):
                        continue
                    question = Question.objects.create(
                        question_type=question_type,
                        subject=subject,
                        class_level=class_level,
                        question_text=q_data.get('question_text', ''),
                        marks=q_data.get('marks', 1),
                        difficulty=difficulty,
                        source='ai_generated',
                        is_approved=False,
                        created_by=request.user,
                        ai_model_used=ai_service.ollama.get_model_name(),
                    )
                    for opt in q_data.get('options', []):
                        MCQOption.objects.create(
                            question=question,
                            option_label=opt.get('label', 'A'),
                            option_text=opt.get('text', ''),
                            is_correct=opt.get('is_correct', False),
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
                    saved_ids.append(str(question.id))
            except Subject.DoesNotExist:
                pass

        return Response(success_response({
            'questions': questions_data,
            'saved_ids': saved_ids,
            'count': len(questions_data),
        }, f'{len(questions_data)} questions generated.'))


class GenerateHolidayPackageView(APIView):
    """Generate a holiday revision package."""
    permission_classes = [IsSuperAdminOrTeacher]
    throttle_scope = 'ai_generation'

    def post(self, request):
        class_level = request.data.get('class_level', 'P4')
        subjects = request.data.get('subjects', [])
        days = min(int(request.data.get('days', 14)), 60)
        student_id = request.data.get('student_id')

        student_profile = {}
        if student_id:
            try:
                from apps.students.models import Student
                student = Student.objects.get(id=student_id)
                profile = getattr(student, 'ai_profile', None)
                if profile:
                    student_profile = {
                        'weak_topics': profile.weak_topics,
                        'strong_topics': profile.strong_topics,
                    }
            except Exception:
                pass

        plan = ai_service.generate_holiday_plan_sync(student_profile, class_level, subjects, days)
        return Response(success_response(plan, 'Holiday plan generated.'))


class AIChatView(APIView):
    """AI tutor chat endpoint for students."""
    permission_classes = [IsStudent]
    throttle_scope = 'ai_generation'

    def post(self, request):
        question = request.data.get('question', '').strip()
        subject = request.data.get('subject', '')
        topic = request.data.get('topic', '')

        if not question:
            return Response({'error': 'question is required.'}, status=400)

        try:
            student = request.user.student_profile
            class_level = student.class_name if student.current_class else 'P4'
        except Exception:
            class_level = 'P4'

        from .prompts import PromptTemplates
        system = PromptTemplates.CHATBOT_SYSTEM.format(class_level=class_level)
        prompt = PromptTemplates.CHATBOT_RESPONSE.format(
            question=question,
            subject=subject,
            topic=topic,
            class_level=class_level,
        )

        response = ai_service.generate_sync(prompt, system, temperature=0.6, max_tokens=512)
        return Response(success_response({
            'answer': response.content,
            'model': response.model,
            'provider': response.provider,
        }))


class AIStatusView(APIView):
    """Check AI provider availability."""
    permission_classes = [IsSuperAdminOrTeacher]

    def get(self, request):
        return Response(success_response({
            'ollama': {
                'available': ai_service.ollama.is_available(),
                'model': ai_service.ollama.get_model_name(),
                'base_url': ai_service.ollama.base_url,
            },
            'openai': {
                'available': ai_service.openai.is_available(),
                'model': ai_service.openai.get_model_name(),
            },
            'gemini': {
                'available': ai_service.gemini.is_available(),
                'model': ai_service.gemini.get_model_name(),
            },
            'primary_provider': ai_service.primary,
        }))


class TriggerMarkingView(APIView):
    """Trigger AI marking for a submitted assessment attempt."""
    permission_classes = [IsSuperAdminOrTeacher]

    def post(self, request):
        attempt_id = request.data.get('attempt_id')
        if not attempt_id:
            return Response({'error': 'attempt_id is required.'}, status=400)
        auto_mark_assessment.delay(attempt_id)
        return Response(success_response({}, 'Marking queued.'))
