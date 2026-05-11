"""Analytics API views."""
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Avg, Count, Sum, Max

from core.permissions import IsSuperAdmin, IsSuperAdminOrTeacher, IsStudent
from core.utils import success_response
from .services import get_student_performance_summary
from .models import SubjectMastery, TopicMastery, DailyActivity


class StudentAnalyticsView(APIView):
    """Full analytics for a specific student."""
    permission_classes = [IsSuperAdminOrTeacher]

    def get(self, request, student_id):
        from apps.students.models import Student
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found.'}, status=404)
        return Response(success_response(get_student_performance_summary(student)))


class MyAnalyticsView(APIView):
    """Student's own analytics."""
    permission_classes = [IsStudent]

    def get(self, request):
        try:
            student = request.user.student_profile
        except Exception:
            return Response({'error': 'Profile not found.'}, status=404)
        return Response(success_response(get_student_performance_summary(student)))


class ClassAnalyticsView(APIView):
    """Analytics for a class — admin/teacher only."""
    permission_classes = [IsSuperAdminOrTeacher]

    def get(self, request, class_id):
        from apps.classes.models import SchoolClass
        from apps.students.models import Student
        from apps.assessments.models import AssessmentAttempt

        try:
            school_class = SchoolClass.objects.get(id=class_id)
        except SchoolClass.DoesNotExist:
            return Response({'error': 'Class not found.'}, status=404)

        students = Student.objects.filter(current_class=school_class, is_active=True)
        attempts = AssessmentAttempt.objects.filter(
            student__in=students,
            status__in=['ai_marked', 'teacher_reviewed', 'published'],
        )

        avg_score = attempts.aggregate(avg=Avg('percentage'))['avg'] or 0
        top_students = students.annotate(
            avg_pct=Avg('attempts__percentage')
        ).order_by('-avg_pct')[:5]

        subject_performance = SubjectMastery.objects.filter(
            student__in=students,
        ).values('subject__name').annotate(avg_mastery=Avg('mastery_score'))

        return Response(success_response({
            'class': {'id': str(school_class.id), 'name': school_class.name},
            'total_students': students.count(),
            'average_score': round(avg_score, 2),
            'total_assessments_taken': attempts.count(),
            'subject_performance': list(subject_performance),
            'top_students': [
                {
                    'name': s.full_name,
                    'admission': s.admission_number,
                    'avg_score': round(getattr(s, 'avg_pct', 0) or 0, 2),
                }
                for s in top_students
            ],
        }))


class AdminDashboardAnalyticsView(APIView):
    """High-level system-wide analytics for admin dashboard."""
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        from apps.students.models import Student
        from apps.teachers.models import Teacher
        from apps.assessments.models import AssessmentAttempt, Assessment
        from apps.question_bank.models import Question
        from django.utils import timezone
        from datetime import timedelta

        today = timezone.now().date()
        week_ago = today - timedelta(days=7)

        total_students = Student.objects.filter(is_active=True).count()
        total_teachers = Teacher.objects.filter(is_active=True).count()
        total_questions = Question.objects.filter(is_active=True).count()
        total_assessments = Assessment.objects.count()

        attempts_this_week = AssessmentAttempt.objects.filter(created_at__date__gte=week_ago)
        active_learners = attempts_this_week.values('student').distinct().count()
        avg_score_week = attempts_this_week.aggregate(avg=Avg('percentage'))['avg'] or 0

        top_performers = Student.objects.annotate(
            avg_score=Avg('attempts__percentage')
        ).filter(avg_score__isnull=False).order_by('-avg_score')[:5]

        struggling = Student.objects.annotate(
            avg_score=Avg('attempts__percentage')
        ).filter(avg_score__lt=40).order_by('avg_score')[:5]

        return Response(success_response({
            'totals': {
                'students': total_students,
                'teachers': total_teachers,
                'questions': total_questions,
                'assessments': total_assessments,
            },
            'this_week': {
                'active_learners': active_learners,
                'attempts': attempts_this_week.count(),
                'average_score': round(avg_score_week, 2),
            },
            'top_performers': [
                {'name': s.full_name, 'class': s.class_name, 'avg_score': round(s.avg_score or 0, 2)}
                for s in top_performers
            ],
            'struggling_learners': [
                {'name': s.full_name, 'class': s.class_name, 'avg_score': round(s.avg_score or 0, 2)}
                for s in struggling
            ],
        }))
