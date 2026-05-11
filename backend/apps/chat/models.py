from django.db import models
from core.models import BaseModel


class ChatMessage(BaseModel):
    sender = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey('users.User', null=True, blank=True, on_delete=models.CASCADE, related_name='received_messages')
    room = models.CharField(max_length=100, blank=True, db_index=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)

    class Meta:
        db_table = 'chat_messages'
        ordering = ['-created_at']
