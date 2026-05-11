"""Holiday learning views."""
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import serializers

from core.permissions import IsSuperAdmin, IsSuperAdminOrTeacher, IsStudent
from core.utils import success_response
from .models import HolidayPackage, StudentHolidayProgress


class HolidayPackageSerializer(serializers.ModelSerializer):
    total_days = serializers.IntegerField(read_only=True)

    class Meta:
        model = HolidayPackage
        fields = ['id', 'title', 'class_level', 'holiday_type', 'start_date', 'end_date',
                  'description', 'is_active', 'is_ai_generated', 'total_days', 'created_at']


class HolidayPackageViewSet(ModelViewSet):
    queryset = HolidayPackage.objects.filter(is_active=True)
    serializer_class = HolidayPackageSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'my_packages', 'my_progress'):
            return [IsStudent()]
        return [IsSuperAdminOrTeacher()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, is_ai_generated=True)

    @action(detail=False, methods=['get'], permission_classes=[IsStudent])
    def my_packages(self, request):
        try:
            student = request.user.student_profile
            class_level = student.current_class.level if student.current_class else None
        except Exception:
            return Response({'error': 'Profile not found.'}, status=404)

        packages = self.get_queryset()
        if class_level:
            packages = packages.filter(class_level=class_level)

        from django.utils import timezone
        today = timezone.now().date()
        packages = packages.filter(end_date__gte=today)

        data = []
        for pkg in packages:
            progress = StudentHolidayProgress.objects.filter(student=student, package=pkg).first()
            pkg_data = HolidayPackageSerializer(pkg).data
            pkg_data['progress'] = {
                'days_completed': getattr(progress, 'days_completed', 0),
                'completion_percentage': getattr(progress, 'completion_percentage', 0),
                'holiday_streak': getattr(progress, 'holiday_streak', 0),
                'current_day': getattr(progress, 'current_day', 1),
            } if progress else None
            data.append(pkg_data)

        return Response(success_response(data))

    @action(detail=True, methods=['post'], permission_classes=[IsSuperAdminOrTeacher])
    def generate_with_ai(self, request, pk=None):
        package = self.get_object()
        from apps.subjects.models import Subject
        subjects = list(Subject.objects.filter(
            class_levels__contains=[package.class_level], is_active=True
        ).values_list('name', flat=True))

        from apps.ai_engine.service import ai_service
        plan = ai_service.generate_holiday_plan_sync({}, package.class_level, subjects, package.total_days)

        return Response(success_response({'plan': plan}, 'AI plan generated.'))
