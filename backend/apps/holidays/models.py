"""Holiday learning package models."""
from django.db import models
from core.models import BaseModel


class HolidayPackage(BaseModel):
    """A holiday revision package for a class level."""
    title = models.CharField(max_length=255)
    class_level = models.CharField(max_length=5)
    holiday_type = models.CharField(
        max_length=20,
        choices=[('term1_end', 'End of Term 1'), ('term2_end', 'End of Term 2'), ('term3_end', 'End of Term 3')],
    )
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    is_ai_generated = models.BooleanField(default=True)
    created_by = models.ForeignKey('users.User', null=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = 'holiday_packages'
        ordering = ['-start_date']

    def __str__(self):
        return f'{self.title} ({self.class_level})'

    @property
    def total_days(self):
        return (self.end_date - self.start_date).days + 1


class HolidayDailyTask(BaseModel):
    """A daily task within a holiday package."""
    package = models.ForeignKey(HolidayPackage, on_delete=models.CASCADE, related_name='daily_tasks')
    day_number = models.PositiveIntegerField()
    date = models.DateField()
    theme = models.CharField(max_length=255)
    daily_goal = models.TextField()

    class Meta:
        db_table = 'holiday_daily_tasks'
        ordering = ['day_number']
        unique_together = ('package', 'day_number')


class HolidayActivity(BaseModel):
    """A single activity within a daily task."""
    daily_task = models.ForeignKey(HolidayDailyTask, on_delete=models.CASCADE, related_name='activities')
    subject = models.ForeignKey('subjects.Subject', null=True, on_delete=models.SET_NULL)
    topic = models.CharField(max_length=255)
    activity_type = models.CharField(
        max_length=20,
        choices=[('revision', 'Revision'), ('practice', 'Practice'), ('quiz', 'Quiz'), ('reading', 'Reading')],
    )
    description = models.TextField()
    duration_minutes = models.PositiveIntegerField(default=20)
    assessment = models.ForeignKey('assessments.Assessment', null=True, blank=True, on_delete=models.SET_NULL)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'holiday_activities'
        ordering = ['order']


class StudentHolidayProgress(models.Model):
    """Tracks a student's progress through a holiday package."""
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE)
    package = models.ForeignKey(HolidayPackage, on_delete=models.CASCADE)
    days_completed = models.PositiveIntegerField(default=0)
    activities_completed = models.PositiveIntegerField(default=0)
    total_score = models.FloatField(default=0)
    completion_percentage = models.FloatField(default=0)
    current_day = models.PositiveIntegerField(default=1)
    holiday_streak = models.PositiveIntegerField(default=0)
    last_activity = models.DateField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'student_holiday_progress'
        unique_together = ('student', 'package')
