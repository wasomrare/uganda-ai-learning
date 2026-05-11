"""Student management views."""
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from core.permissions import IsSuperAdmin, IsSuperAdminOrTeacher, IsStudent
from core.utils import success_response
from .models import Student, ParentGuardian, StudentAIProfile
from .serializers import (
    StudentListSerializer, StudentDetailSerializer,
    CreateStudentSerializer, ParentGuardianSerializer,
    StudentAIProfileSerializer,
)


class StudentViewSet(ModelViewSet):
    queryset = Student.objects.select_related(
        'user', 'current_class', 'ai_profile'
    ).prefetch_related('parents').all()

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['current_class', 'is_active', 'gender', 'stream']
    search_fields = ['user__first_name', 'user__last_name', 'admission_number', 'user__username']
    ordering_fields = ['created_at', 'user__last_name', 'admission_number']
    ordering = ['user__last_name']

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsSuperAdminOrTeacher()]
        if self.action == 'my_profile':
            return [IsStudent()]
        return [IsSuperAdmin()]

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateStudentSerializer
        if self.action == 'list':
            return StudentListSerializer
        return StudentDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = CreateStudentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        student = serializer.save()
        return Response(success_response({
            'student': StudentDetailSerializer(student).data,
            'temporary_password': getattr(student, '_temp_password', None),
        }, 'Student created successfully.'), status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], permission_classes=[IsStudent])
    def my_profile(self, request):
        try:
            student = request.user.student_profile
            return Response(success_response(StudentDetailSerializer(student).data))
        except Student.DoesNotExist:
            return Response({'error': 'Student profile not found.'}, status=404)

    @action(detail=True, methods=['get'], permission_classes=[IsSuperAdminOrTeacher])
    def performance(self, request, pk=None):
        student = self.get_object()
        from apps.analytics.services import get_student_performance_summary
        summary = get_student_performance_summary(student)
        return Response(success_response(summary))

    @action(detail=True, methods=['post'], permission_classes=[IsSuperAdmin])
    def toggle_active(self, request, pk=None):
        student = self.get_object()
        student.is_active = not student.is_active
        student.save()
        student.user.is_active = student.is_active
        student.user.save()
        return Response(success_response(
            {}, f'Student {"activated" if student.is_active else "deactivated"}.'
        ))

    @action(detail=True, methods=['get'], permission_classes=[IsSuperAdminOrTeacher])
    def ai_profile(self, request, pk=None):
        student = self.get_object()
        profile, _ = StudentAIProfile.objects.get_or_create(student=student)
        return Response(success_response(StudentAIProfileSerializer(profile).data))

    @action(detail=False, methods=['get'], permission_classes=[IsSuperAdmin])
    def stats(self, request):
        from django.db.models import Count
        total = Student.objects.count()
        active = Student.objects.filter(is_active=True).count()
        by_class = list(
            Student.objects.values('current_class__name').annotate(count=Count('id'))
        )
        return Response(success_response({
            'total': total,
            'active': active,
            'inactive': total - active,
            'by_class': by_class,
        }))
