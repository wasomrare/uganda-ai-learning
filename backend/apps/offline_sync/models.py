"""Offline sync queue models."""
from django.db import models
from core.models import BaseModel


class SyncQueue(BaseModel):
    """Queue for offline data waiting to be synced to server."""
    SYNC_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('synced', 'Synced'),
        ('failed', 'Failed'),
        ('conflict', 'Conflict'),
    ]

    ENTITY_TYPES = [
        ('assessment_attempt', 'Assessment Attempt'),
        ('student_answer', 'Student Answer'),
        ('daily_activity', 'Daily Activity'),
        ('gamification', 'Gamification Event'),
    ]

    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='sync_queue')
    entity_type = models.CharField(max_length=30, choices=ENTITY_TYPES)
    entity_id = models.CharField(max_length=100)
    payload = models.JSONField()
    status = models.CharField(max_length=20, choices=SYNC_STATUS, default='pending', db_index=True)
    retry_count = models.PositiveIntegerField(default=0)
    max_retries = models.PositiveIntegerField(default=3)
    error_message = models.TextField(blank=True)
    synced_at = models.DateTimeField(null=True, blank=True)
    device_id = models.CharField(max_length=255, blank=True)
    offline_created_at = models.DateTimeField()

    class Meta:
        db_table = 'sync_queue'
        ordering = ['created_at']
        indexes = [models.Index(fields=['student', 'status'])]
