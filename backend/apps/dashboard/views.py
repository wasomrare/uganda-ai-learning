"""Dashboard aggregate views."""
from rest_framework.views import APIView
from rest_framework.response import Response

from core.permissions import IsSuperAdmin, IsSuperAdminOrTeacher, IsStudent
from core.utils import success_response


class AdminDashboardView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        from apps.analytics.views import AdminDashboardAnalyticsView
        return AdminDashboardAnalyticsView().get(request)


class TeacherDashboardView(APIView):
    permission_classes = [IsSuperAdminOrTeacher]

    def get(self, request):
        try:
            teacher = request.user.teacher_profile
        except Exception:
            return Response({'error': 'Teacher profile not found.'}, status=404)

        from apps.classes.models import SchoolClass
        from apps.assessments.models import AssessmentAttempt, Assessment
        from apps.students.models import Student
        from django.db.models import Avg

        classes = teacher.classes.filter(is_active=True)
        students_count = Student.objects.filter(current_class__in=classes, is_active=True).count()
        pending_marking = AssessmentAttempt.objects.filter(
            assessment__subject__in=teacher.subjects.all(),
            status='ai_marked',
        ).count()

        return Response(success_response({
            'teacher': {'name': teacher.full_name, 'employee_number': teacher.employee_number},
            'classes': [{'id': str(c.id), 'name': c.name} for c in classes],
            'students_count': students_count,
            'pending_marking': pending_marking,
        }))


class StudentDashboardView(APIView):
    permission_classes = [IsStudent]

    def get(self, request):
        try:
            student = request.user.student_profile
        except Exception:
            return Response({'error': 'Profile not found.'}, status=404)

        from apps.analytics.services import get_student_performance_summary
        from apps.gamification.models import StudentXP, Streak
        from apps.recommendations.models import LearningRecommendation
        from apps.assessments.models import Assessment

        summary = get_student_performance_summary(student)
        xp = StudentXP.objects.filter(student=student).first()
        streak = Streak.objects.filter(student=student).first()
        rec_count = LearningRecommendation.objects.filter(student=student, is_completed=False).count()

        active_assessments = Assessment.objects.filter(
            class_level=student.current_class.level if student.current_class else '',
            status='active',
        ).count()

        return Response(success_response({
            'student': {
                'name': student.full_name,
                'class': student.class_name,
                'admission': student.admission_number,
            },
            'performance': {
                'average_score': summary.get('average_score', 0),
                'total_attempts': summary.get('total_attempts', 0),
                'overall_mastery': summary.get('overall_mastery', 0),
                'ple_readiness': summary.get('ple_readiness_score', 0),
            },
            'gamification': {
                'total_xp': getattr(xp, 'total_xp', 0),
                'level': getattr(xp, 'level', 1),
                'coins': getattr(xp, 'coins', 0),
            },
            'streak': {
                'current': getattr(streak, 'current_streak', 0),
                'longest': getattr(streak, 'longest_streak', 0),
            },
            'recommendations_count': rec_count,
            'active_assessments': active_assessments,
        }))
