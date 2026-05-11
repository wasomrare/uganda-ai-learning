"""WebSocket consumer for live classes."""
import json
from channels.generic.websocket import AsyncWebsocketConsumer


class LiveClassConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.group_name = f'live_class_{self.room_id}'
        user = self.scope.get('user')
        if not user or not user.is_authenticated:
            await self.close()
            return
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.channel_layer.group_send(self.group_name, {
            'type': 'user_joined',
            'user': user.get_full_name(),
            'role': user.role,
        })

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        msg_type = data.get('type', 'chat')
        user = self.scope.get('user')
        await self.channel_layer.group_send(self.group_name, {
            'type': 'class_message',
            'message_type': msg_type,
            'content': data.get('content', ''),
            'sender': user.get_full_name() if user else 'Unknown',
            'role': user.role if user else 'unknown',
        })

    async def class_message(self, event):
        await self.send(text_data=json.dumps(event))

    async def user_joined(self, event):
        await self.send(text_data=json.dumps({'type': 'user_joined', **event}))
