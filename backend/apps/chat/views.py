from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers
from core.utils import success_response
from .models import ChatMessage


class ChatHistoryView(APIView):
    def get(self, request, room):
        messages = ChatMessage.objects.filter(room=room).select_related('sender').order_by('-created_at')[:50]
        return Response(success_response([{
            'id': str(m.id),
            'sender': m.sender.get_full_name(),
            'message': m.message,
            'timestamp': m.created_at.isoformat(),
        } for m in reversed(list(messages))]))
