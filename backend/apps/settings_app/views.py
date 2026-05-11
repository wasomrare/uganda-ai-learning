from rest_framework.views import APIView
from rest_framework.response import Response
from core.permissions import IsSuperAdmin
from core.utils import success_response
from .models import SystemSetting


class SystemSettingsView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        settings = SystemSetting.objects.all()
        return Response(success_response([{
            'key': s.key, 'value': s.value, 'description': s.description
        } for s in settings]))

    def post(self, request):
        key = request.data.get('key')
        value = request.data.get('value')
        if not key or value is None:
            return Response({'error': 'key and value are required.'}, status=400)
        setting, _ = SystemSetting.objects.update_or_create(
            key=key, defaults={'value': str(value)}
        )
        return Response(success_response({'key': setting.key, 'value': setting.value}, 'Setting saved.'))
