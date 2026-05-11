from django.db import models
from core.models import BaseModel


class Report(BaseModel):
    REPORT_TYPES = [
        ('student_report_card', 'Student Report Card'),
        ('class_report', 'Class Report'),
        ('exam_report', 'Exam Report'),
        ('analytics_report', 'Analytics Report'),
        ('holiday_report', 'Holiday Report'),
        ('leaderboard_report', 'Leaderboard Report'),
    ]

    title = models.CharField(max_length=255)
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES)
    generated_by = models.ForeignKey('users.User', null=True, on_delete=models.SET_NULL)
    file = models.FileField(upload_to='reports/', null=True, blank=True)
    parameters = models.JSONField(default=dict)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('ready', 'Ready'), ('failed', 'Failed')],
        default='pending',
    )

    class Meta:
        db_table = 'reports'
        ordering = ['-created_at']
