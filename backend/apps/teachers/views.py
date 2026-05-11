"""Teacher management views."""
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from core.permissions import IsSuperAdmin, IsSuperAdminOrTeacher, IsTeacher
from core.utils import success_response
from .models import Teacher
from .serializers import TeacherListSerializer, TeacherDetailSerializer, CreateTeacherSerializer


class TeacherViewSet(ModelViewSet):
    queryset = Teacher.objects.select_related('user').prefetch_related('classes', 'subjects').all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'is_class_teacher']
    search_fields = ['user__first_name', 'user__last_name', 'employee_number', 'user__username']
    ordering_fields = ['created_at', 'user__last_name']
    ordering = ['user__last_name']

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsSuperAdminOrTeacher()]
        if self.action == 'my_profile':
            return [IsTeacher()]
        return [IsSuperAdmin()]

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateTeacherSerializer
        if self.action == 'list':
            return TeacherListSerializer
        return TeacherDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = CreateTeacherSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        teacher = serializer.save()
        return Response(success_response({
            'teacher': TeacherDetailSerializer(teacher).data,
            'temporary_password': getattr(teacher, '_temp_password', None),
        }, 'Teacher created successfully.'), status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], permission_classes=[IsTeacher])
    def my_profile(self, request):
        try:
            teacher = request.user.teacher_profile
            return Response(success_response(TeacherDetailSerializer(teacher).data))
        except Teacher.DoesNotExist:
            return Response({'error': 'Teacher profile not found.'}, status=404)

    @action(detail=True, methods=['post'], permission_classes=[IsSuperAdmin])
    def assign_classes(self, request, pk=None):
        teacher = self.get_object()
        class_ids = request.data.get('class_ids', [])
        from apps.classes.models import SchoolClass
        classes = SchoolClass.objects.filter(id__in=class_ids)
        teacher.classes.set(classes)
        return Response(success_response({}, 'Classes assigned.'))

    @action(detail=True, methods=['post'], permission_classes=[IsSuperAdmin])
    def assign_subjects(self, request, pk=None):
        teacher = self.get_object()
        subject_ids = request.data.get('subject_ids', [])
        from apps.subjects.models import Subject
        subjects = Subject.objects.filter(id__in=subject_ids)
        teacher.subjects.set(subjects)
        return Response(success_response({}, 'Subjects assigned.'))

    @action(detail=True, methods=['post'], permission_classes=[IsSuperAdmin])
    def toggle_active(self, request, pk=None):
        teacher = self.get_object()
        teacher.is_active = not teacher.is_active
        teacher.save()
        teacher.user.is_active = teacher.is_active
        teacher.user.save()
        return Response(success_response(
            {}, f'Teacher {"activated" if teacher.is_active else "deactivated"}.'
        ))
