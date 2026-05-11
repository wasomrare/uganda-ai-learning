"""Notification models."""
from django.db import models
from core.models import BaseModel


class Notification(BaseModel):
    NOTIFICATION_TYPE = [
        ('assignment', 'New Assignment'),
        ('result', 'Result Published'),
        ('achievement', 'Achievement Unlocked'),
        ('reminder', 'Revision Reminder'),
        ('announcement', 'School Announcement'),
        ('live_class', 'Live Class'),
        ('streak', 'Streak Alert'),
        ('ai_ready', 'AI Content Ready'),
    ]

    recipient = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPE)
    title = models.CharField(max_length=255)
    body = models.TextField()
    data = models.JSONField(default=dict)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    sent_push = models.BooleanField(default=False)
    sent_email = models.BooleanField(default=False)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [models.Index(fields=['recipient', 'is_read'])]

    def __str__(self):
        return f'{self.title} → {self.recipient.username}'


class Announcement(BaseModel):
    """School-wide announcements from admin."""
    title = models.CharField(max_length=255)
    body = models.TextField()
    target_roles = models.JSONField(default=list)
    target_classes = models.ManyToManyField('classes.SchoolClass', blank=True)
    is_pinned = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey('users.User', on_delete=models.CASCADE)

    class Meta:
        db_table = 'announcements'
        ordering = ['-created_at']
