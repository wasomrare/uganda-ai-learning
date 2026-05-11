"""Live class session models."""
from django.db import models
from core.models import BaseModel


class LiveClass(BaseModel):
    STATUS_CHOICES = [('scheduled', 'Scheduled'), ('live', 'Live'), ('ended', 'Ended'), ('cancelled', 'Cancelled')]

    title = models.CharField(max_length=255)
    teacher = models.ForeignKey('teachers.Teacher', on_delete=models.CASCADE, related_name='live_classes')
    school_class = models.ForeignKey('classes.SchoolClass', on_delete=models.CASCADE, related_name='live_classes')
    subject = models.ForeignKey('subjects.Subject', null=True, on_delete=models.SET_NULL)
    scheduled_at = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=45)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    meeting_url = models.URLField(blank=True)
    room_id = models.CharField(max_length=100, unique=True, blank=True)
    recording_url = models.URLField(blank=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'live_classes'
        ordering = ['-scheduled_at']

    def __str__(self):
        return f'{self.title} — {self.teacher.full_name}'


class LiveClassAttendance(models.Model):
    live_class = models.ForeignKey(LiveClass, on_delete=models.CASCADE, related_name='attendances')
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'live_class_attendances'
        unique_together = ('live_class', 'student')
