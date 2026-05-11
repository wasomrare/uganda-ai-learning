from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers
from core.permissions import IsSuperAdmin
from core.utils import success_response
from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = AuditLog
        fields = ['id', 'username', 'action', 'path', 'ip_address', 'status_code', 'timestamp']


class AuditLogView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        logs = AuditLog.objects.select_related('user').all()[:200]
        return Response(success_response(AuditLogSerializer(logs, many=True).data))
