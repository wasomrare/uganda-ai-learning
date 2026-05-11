"""Offline sync views."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers
from django.utils import timezone

from core.permissions import IsStudent
from core.utils import success_response
from .models import SyncQueue


class SyncQueueSerializer(serializers.ModelSerializer):
    class Meta:
        model = SyncQueue
        fields = ['id', 'entity_type', 'entity_id', 'payload', 'status',
                  'retry_count', 'error_message', 'offline_created_at']


class SyncUploadView(APIView):
    """Receive offline data from Flutter app and queue for processing."""
    permission_classes = [IsStudent]

    def post(self, request):
        try:
            student = request.user.student_profile
        except Exception:
            return Response({'error': 'Student not found.'}, status=404)

        items = request.data.get('items', [])
        if not items:
            return Response({'error': 'No items to sync.'}, status=400)

        created = 0
        for item in items:
            entity_type = item.get('entity_type')
            entity_id = item.get('entity_id', '')
            payload = item.get('payload', {})
            offline_ts = item.get('offline_created_at', timezone.now().isoformat())

            if not entity_type:
                continue

            if not SyncQueue.objects.filter(student=student, entity_id=entity_id, entity_type=entity_type, status='synced').exists():
                SyncQueue.objects.create(
                    student=student,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    payload=payload,
                    device_id=request.META.get('HTTP_X_DEVICE_ID', ''),
                    offline_created_at=offline_ts,
                )
                created += 1

        return Response(success_response({'queued': created}, f'{created} items queued for sync.'))


class SyncStatusView(APIView):
    """Check sync queue status for a student."""
    permission_classes = [IsStudent]

    def get(self, request):
        try:
            student = request.user.student_profile
        except Exception:
            return Response({'error': 'Student not found.'}, status=404)

        queue = SyncQueue.objects.filter(student=student)
        return Response(success_response({
            'pending': queue.filter(status='pending').count(),
            'processing': queue.filter(status='processing').count(),
            'synced': queue.filter(status='synced').count(),
            'failed': queue.filter(status='failed').count(),
        }))


class OfflineDataDownloadView(APIView):
    """Provide lightweight cached data for offline use."""
    permission_classes = [IsStudent]

    def get(self, request):
        try:
            student = request.user.student_profile
        except Exception:
            return Response({'error': 'Student not found.'}, status=404)

        class_level = student.current_class.level if student.current_class else 'P4'

        from apps.curriculum.models import Topic
        from apps.question_bank.models import Question

        topics = Topic.objects.filter(
            class_level=class_level, is_active=True
        ).select_related('subject').values(
            'id', 'name', 'subject__name', 'class_level', 'term', 'week'
        )[:50]

        questions = Question.objects.filter(
            class_level=class_level, is_approved=True, is_active=True
        ).values(
            'id', 'question_type', 'question_text', 'difficulty', 'marks'
        )[:100]

        return Response(success_response({
            'class_level': class_level,
            'topics': list(topics),
            'questions': list(questions),
            'cached_at': timezone.now().isoformat(),
        }))
