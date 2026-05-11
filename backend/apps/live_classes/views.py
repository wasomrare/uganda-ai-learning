"""Live class views."""
import secrets
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import serializers

from core.permissions import IsSuperAdminOrTeacher, IsStudent
from core.utils import success_response
from .models import LiveClass, LiveClassAttendance


class LiveClassSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True)
    class_name = serializers.CharField(source='school_class.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)

    class Meta:
        model = LiveClass
        fields = ['id', 'title', 'teacher_name', 'class_name', 'subject_name',
                  'scheduled_at', 'duration_minutes', 'status', 'meeting_url',
                  'room_id', 'recording_url', 'description', 'created_at']


class LiveClassViewSet(ModelViewSet):
    queryset = LiveClass.objects.select_related('teacher__user', 'school_class', 'subject').all()
    serializer_class = LiveClassSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'join'):
            return [IsStudent()]
        return [IsSuperAdminOrTeacher()]

    def perform_create(self, serializer):
        room_id = secrets.token_urlsafe(12)
        try:
            teacher = self.request.user.teacher_profile
        except Exception:
            teacher = None
        serializer.save(room_id=room_id, teacher=teacher)

    @action(detail=True, methods=['post'], permission_classes=[IsSuperAdminOrTeacher])
    def start(self, request, pk=None):
        live_class = self.get_object()
        live_class.status = 'live'
        live_class.save()
        return Response(success_response({'room_id': live_class.room_id, 'ws_url': f'/ws/live-class/{live_class.room_id}/'}, 'Class started.'))

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        live_class = self.get_object()
        if live_class.status != 'live':
            return Response({'error': 'Class is not live yet.'}, status=400)
        try:
            student = request.user.student_profile
            LiveClassAttendance.objects.get_or_create(live_class=live_class, student=student)
        except Exception:
            pass
        return Response(success_response({'room_id': live_class.room_id, 'ws_url': f'/ws/live-class/{live_class.room_id}/'}, 'Joined class.'))

    @action(detail=True, methods=['post'], permission_classes=[IsSuperAdminOrTeacher])
    def end(self, request, pk=None):
        live_class = self.get_object()
        live_class.status = 'ended'
        live_class.save()
        return Response(success_response({}, 'Class ended.'))
