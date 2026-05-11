"""Notification views."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers
from django.utils import timezone

from core.permissions import IsSuperAdmin, IsSuperAdminOrTeacher, IsStudent
from core.utils import success_response
from .models import Notification, Announcement


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'title', 'body', 'data', 'is_read', 'read_at', 'created_at']


class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ['id', 'title', 'body', 'is_pinned', 'expires_at', 'created_at']


class MyNotificationsView(APIView):
    permission_classes = [IsStudent]

    def get(self, request):
        notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')[:50]
        unread_count = notifications.filter(is_read=False).count()
        return Response(success_response({
            'unread_count': unread_count,
            'notifications': NotificationSerializer(notifications, many=True).data,
        }))

    def post(self, request):
        """Mark notifications as read."""
        ids = request.data.get('ids', [])
        if ids:
            Notification.objects.filter(recipient=request.user, id__in=ids).update(
                is_read=True, read_at=timezone.now()
            )
        else:
            Notification.objects.filter(recipient=request.user, is_read=False).update(
                is_read=True, read_at=timezone.now()
            )
        return Response(success_response({}, 'Marked as read.'))


class AdminBroadcastView(APIView):
    """Admin broadcasts announcement to all users."""
    permission_classes = [IsSuperAdmin]

    def post(self, request):
        title = request.data.get('title', '')
        body = request.data.get('body', '')
        target_roles = request.data.get('target_roles', ['student', 'teacher'])
        is_pinned = request.data.get('is_pinned', False)

        if not title or not body:
            return Response({'error': 'title and body are required.'}, status=400)

        announcement = Announcement.objects.create(
            title=title, body=body,
            target_roles=target_roles,
            is_pinned=is_pinned,
            created_by=request.user,
        )

        from apps.users.models import User
        recipients = User.objects.filter(role__in=target_roles, is_active=True)
        notifications = [
            Notification(
                recipient=user,
                notification_type='announcement',
                title=title, body=body,
                data={'announcement_id': str(announcement.id)},
            )
            for user in recipients
        ]
        Notification.objects.bulk_create(notifications, batch_size=200)

        return Response(success_response(
            {'announcement_id': str(announcement.id), 'recipients': len(notifications)},
            'Announcement broadcast sent.'
        ))


class AnnouncementsView(APIView):
    permission_classes = [IsSuperAdminOrTeacher]

    def get(self, request):
        announcements = Announcement.objects.order_by('-created_at')[:20]
        return Response(success_response(AnnouncementSerializer(announcements, many=True).data))
