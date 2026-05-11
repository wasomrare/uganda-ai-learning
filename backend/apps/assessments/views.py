"""Assessment views — CRUD, student attempts, teacher marking."""
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from core.permissions import IsSuperAdmin, IsSuperAdminOrTeacher, IsStudent
from core.utils import success_response, calculate_percentage
from .models import Assessment, AssessmentAttempt, StudentAnswer, AssessmentQuestion
from .serializers import (
    AssessmentListSerializer, AssessmentDetailSerializer,
    SubmitAssessmentSerializer, AttemptResultSerializer,
    TeacherMarkingSerializer,
)


class AssessmentViewSet(ModelViewSet):
    queryset = Assessment.objects.select_related('subject', 'school_class').all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['assessment_type', 'class_level', 'subject', 'status', 'term']
    search_fields = ['title', 'description']
    ordering_fields = ['-created_at', 'scheduled_start', 'total_marks']
    ordering = ['-created_at']

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'publish', 'mark_review'):
            return [IsSuperAdminOrTeacher()]
        if self.action in ('student_assessments', 'start_attempt', 'submit_attempt'):
            return [IsStudent()]
        return [IsSuperAdminOrTeacher()]

    def get_serializer_class(self):
        if self.action == 'list':
            return AssessmentListSerializer
        return AssessmentDetailSerializer

    def perform_create(self, serializer):
        from django.utils import timezone
        serializer.save(created_by=self.request.user, academic_year=timezone.now().year)

    @action(detail=True, methods=['post'], permission_classes=[IsSuperAdminOrTeacher])
    def publish(self, request, pk=None):
        assessment = self.get_object()
        if not assessment.questions.filter(is_approved=True).exists():
            return Response({'error': 'No approved questions. Add questions first.'}, status=400)
        assessment.status = 'active'
        assessment.save()
        return Response(success_response({}, 'Assessment published.'))

    @action(detail=True, methods=['post'], permission_classes=[IsSuperAdminOrTeacher])
    def archive(self, request, pk=None):
        assessment = self.get_object()
        assessment.status = 'archived'
        assessment.save()
        return Response(success_response({}, 'Assessment archived.'))

    @action(detail=False, methods=['get'], permission_classes=[IsStudent])
    def student_assessments(self, request):
        try:
            student = request.user.student_profile
        except Exception:
            return Response({'error': 'Student profile not found.'}, status=404)

        assessments = self.get_queryset().filter(
            class_level=student.class_name if student.current_class else '',
            status='active',
        )
        return Response(success_response(AssessmentListSerializer(assessments, many=True).data))

    @action(detail=True, methods=['post'], permission_classes=[IsStudent])
    def start_attempt(self, request, pk=None):
        assessment = self.get_object()

        if assessment.status != 'active':
            return Response({'error': 'This assessment is not currently active.'}, status=400)

        try:
            student = request.user.student_profile
        except Exception:
            return Response({'error': 'Student profile not found.'}, status=404)

        existing = AssessmentAttempt.objects.filter(
            assessment=assessment, student=student, status='in_progress'
        ).first()
        if existing:
            return Response(success_response({'attempt_id': str(existing.id)}, 'Resuming existing attempt.'))

        attempt_count = AssessmentAttempt.objects.filter(
            assessment=assessment, student=student
        ).count()
        if attempt_count >= assessment.max_attempts:
            return Response({'error': 'Maximum attempts reached.'}, status=400)

        attempt = AssessmentAttempt.objects.create(
            assessment=assessment,
            student=student,
            attempt_number=attempt_count + 1,
            ip_address=request.META.get('REMOTE_ADDR', ''),
            device_id=request.META.get('HTTP_X_DEVICE_ID', ''),
        )

        questions = assessment.assessment_questions.select_related('question').order_by('order')
        from apps.question_bank.serializers import QuestionStudentSerializer
        import random
        q_list = [aq.question for aq in questions]
        if assessment.shuffle_questions:
            random.shuffle(q_list)

        return Response(success_response({
            'attempt_id': str(attempt.id),
            'duration_minutes': assessment.duration_minutes,
            'total_marks': assessment.total_marks,
            'questions': QuestionStudentSerializer(q_list, many=True).data,
            'instructions': assessment.instructions,
        }))

    @action(detail=True, methods=['post'], permission_classes=[IsStudent])
    def submit_attempt(self, request, pk=None):
        assessment = self.get_object()
        serializer = SubmitAssessmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            student = request.user.student_profile
            attempt = AssessmentAttempt.objects.get(
                assessment=assessment, student=student, status='in_progress'
            )
        except Exception as e:
            return Response({'error': 'No active attempt found.'}, status=400)

        for ans_data in serializer.validated_data['answers']:
            try:
                from apps.question_bank.models import Question, MCQOption
                question = Question.objects.get(id=ans_data['question_id'])
                student_answer, _ = StudentAnswer.objects.get_or_create(
                    attempt=attempt, question=question
                )
                if ans_data.get('selected_option_id'):
                    student_answer.selected_option_id = ans_data['selected_option_id']
                student_answer.text_answer = ans_data.get('text_answer', '')
                student_answer.matching_answer = ans_data.get('matching_answer', {})
                student_answer.drag_drop_answer = ans_data.get('drag_drop_answer', [])
                student_answer.arrangement_answer = ans_data.get('arrangement_answer', [])
                student_answer.time_taken_seconds = ans_data.get('time_taken_seconds', 0)
                student_answer.hint_used = ans_data.get('hint_used', False)
                student_answer.save()
            except Exception:
                continue

        attempt.status = 'submitted'
        attempt.submitted_at = timezone.now()
        attempt.time_taken_seconds = serializer.validated_data.get('time_taken_seconds', 0)
        attempt.save()

        from apps.ai_engine.tasks import auto_mark_assessment
        auto_mark_assessment.delay(str(attempt.id))

        return Response(success_response(
            {'attempt_id': str(attempt.id), 'status': 'submitted'},
            'Assessment submitted. Marking in progress.'
        ))

    @action(detail=True, methods=['get'], permission_classes=[IsStudent])
    def my_results(self, request, pk=None):
        assessment = self.get_object()
        try:
            student = request.user.student_profile
            attempts = AssessmentAttempt.objects.filter(
                assessment=assessment, student=student
            ).order_by('-created_at')
            return Response(success_response(AttemptResultSerializer(attempts, many=True).data))
        except Exception:
            return Response({'error': 'Profile not found.'}, status=404)

    @action(detail=True, methods=['post'], permission_classes=[IsSuperAdminOrTeacher])
    def teacher_mark(self, request, pk=None):
        """Teacher reviews/overrides AI marks."""
        attempt_id = request.data.get('attempt_id')
        markings = request.data.get('markings', [])

        try:
            attempt = AssessmentAttempt.objects.get(id=attempt_id)
        except AssessmentAttempt.DoesNotExist:
            return Response({'error': 'Attempt not found.'}, status=404)

        total_teacher_score = 0
        for mark in markings:
            try:
                answer = StudentAnswer.objects.get(id=mark['answer_id'])
                answer.teacher_score = mark['teacher_score']
                answer.teacher_comment = mark.get('teacher_comment', '')
                answer.final_score = mark['teacher_score']
                answer.save()
                total_teacher_score += mark['teacher_score']
            except StudentAnswer.DoesNotExist:
                continue

        attempt.teacher_score = total_teacher_score
        attempt.final_score = total_teacher_score
        attempt.percentage = calculate_percentage(total_teacher_score, attempt.assessment.total_marks)
        attempt.is_passed = attempt.final_score >= attempt.assessment.passing_marks
        attempt.teacher_comment = request.data.get('overall_comment', '')
        attempt.status = 'teacher_reviewed'
        attempt.save()

        return Response(success_response({}, 'Marks updated.'))
