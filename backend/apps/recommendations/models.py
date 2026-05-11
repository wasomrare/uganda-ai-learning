"""Recommendation models."""
from django.db import models
from core.models import BaseModel


class LearningRecommendation(BaseModel):
    TYPES = [
        ('practice', 'Practice More'),
        ('revision', 'Revise Topic'),
        ('challenge', 'Try Challenge'),
        ('resource', 'Read Resource'),
        ('assessment', 'Take Assessment'),
    ]

    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='recommendations')
    recommendation_type = models.CharField(max_length=20, choices=TYPES)
    subject = models.ForeignKey('subjects.Subject', null=True, blank=True, on_delete=models.SET_NULL)
    topic = models.ForeignKey('curriculum.Topic', null=True, blank=True, on_delete=models.SET_NULL)
    message = models.TextField()
    priority = models.CharField(max_length=10, choices=[('high', 'High'), ('medium', 'Medium'), ('low', 'Low')], default='medium')
    estimated_time_minutes = models.PositiveIntegerField(default=15)
    is_completed = models.BooleanField(default=False)
    ai_generated = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'learning_recommendations'
        ordering = ['-created_at']
