"""Revision session models."""
from django.db import models
from core.models import BaseModel


class RevisionSession(BaseModel):
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='revision_sessions')
    subject = models.ForeignKey('subjects.Subject', null=True, on_delete=models.SET_NULL)
    topic = models.ForeignKey('curriculum.Topic', null=True, blank=True, on_delete=models.SET_NULL)
    score = models.FloatField(default=0)
    questions_attempted = models.PositiveIntegerField(default=0)
    questions_correct = models.PositiveIntegerField(default=0)
    duration_minutes = models.PositiveIntegerField(default=0)
    is_ai_generated = models.BooleanField(default=True)

    class Meta:
        db_table = 'revision_sessions'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.student.full_name} — {self.subject}'
