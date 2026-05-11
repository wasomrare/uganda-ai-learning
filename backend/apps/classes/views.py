"""School class views."""
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.permissions import IsSuperAdmin, IsSuperAdminOrTeacher
from core.utils import success_response
from .models import SchoolClass


class SchoolClassSerializer(serializers.ModelSerializer):
    student_count = serializers.IntegerField(read_only=True)
    class_teacher_name = serializers.SerializerMethodField()

    class Meta:
        model = SchoolClass
        fields = [
            'id', 'name', 'level', 'stream', 'academic_year', 'term',
            'class_teacher', 'class_teacher_name', 'capacity',
            'student_count', 'is_active', 'is_lower_primary', 'is_upper_primary',
            'created_at',
        ]

    def get_class_teacher_name(self, obj):
        if obj.class_teacher:
            return obj.class_teacher.full_name
        return None


class SchoolClassViewSet(ModelViewSet):
    queryset = SchoolClass.objects.select_related('class_teacher__user').all()
    serializer_class = SchoolClassSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsSuperAdminOrTeacher()]
        return [IsSuperAdmin()]

    @action(detail=True, methods=['get'], permission_classes=[IsSuperAdminOrTeacher])
    def students(self, request, pk=None):
        school_class = self.get_object()
        from apps.students.serializers import StudentListSerializer
        students = school_class.students.select_related('user').filter(is_active=True)
        return Response(success_response(StudentListSerializer(students, many=True).data))

    @action(detail=True, methods=['get'], permission_classes=[IsSuperAdminOrTeacher])
    def subjects(self, request, pk=None):
        school_class = self.get_object()
        from apps.subjects.models import Subject
        subjects = Subject.objects.filter(class_levels__contains=[school_class.level])
        from apps.subjects.serializers import SubjectSerializer
        return Response(success_response(SubjectSerializer(subjects, many=True).data))
