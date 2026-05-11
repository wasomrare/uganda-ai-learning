import json
from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room = self.scope['url_route']['kwargs']['room']
        self.group_name = f'chat_{self.room}'
        user = self.scope.get('user')
        if not user or not user.is_authenticated:
            await self.close()
            return
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        user = self.scope.get('user')
        await self.channel_layer.group_send(self.group_name, {
            'type': 'chat_message',
            'message': data.get('message', ''),
            'sender': user.get_full_name() if user else 'Unknown',
            'sender_role': user.role if user else 'unknown',
        })

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))
