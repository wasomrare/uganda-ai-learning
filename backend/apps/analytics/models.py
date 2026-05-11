"""Analytics models — performance tracking, mastery, engagement."""
from django.db import models
from core.models import BaseModel


class SubjectMastery(BaseModel):
    """Tracks a student's mastery level per subject."""
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='subject_masteries')
    subject = models.ForeignKey('subjects.Subject', on_delete=models.CASCADE, related_name='mastery_records')
    class_level = models.CharField(max_length=5)
    mastery_score = models.FloatField(default=0.0)
    attempts = models.PositiveIntegerField(default=0)
    correct = models.PositiveIntegerField(default=0)
    total_time_spent_minutes = models.PositiveIntegerField(default=0)
    last_practiced = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'subject_mastery'
        unique_together = ('student', 'subject', 'class_level')

    @property
    def accuracy(self):
        return round((self.correct / self.attempts * 100), 2) if self.attempts else 0.0


class TopicMastery(BaseModel):
    """Tracks mastery per topic."""
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='topic_masteries')
    topic = models.ForeignKey('curriculum.Topic', on_delete=models.CASCADE, related_name='mastery_records')
    mastery_score = models.FloatField(default=0.0)
    attempts = models.PositiveIntegerField(default=0)
    correct = models.PositiveIntegerField(default=0)
    last_practiced = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'topic_mastery'
        unique_together = ('student', 'topic')


class DailyActivity(models.Model):
    """Daily engagement tracking per student."""
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='daily_activities')
    date = models.DateField(db_index=True)
    questions_attempted = models.PositiveIntegerField(default=0)
    questions_correct = models.PositiveIntegerField(default=0)
    time_spent_minutes = models.PositiveIntegerField(default=0)
    assessments_taken = models.PositiveIntegerField(default=0)
    xp_earned = models.PositiveIntegerField(default=0)
    login_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'daily_activity'
        unique_together = ('student', 'date')
        ordering = ['-date']


class AssessmentAnalytics(BaseModel):
    """Aggregated analytics for a specific assessment."""
    assessment = models.OneToOneField('assessments.Assessment', on_delete=models.CASCADE, related_name='analytics')
    total_attempts = models.PositiveIntegerField(default=0)
    completed_attempts = models.PositiveIntegerField(default=0)
    average_score = models.FloatField(default=0)
    highest_score = models.FloatField(default=0)
    lowest_score = models.FloatField(default=0)
    pass_rate = models.FloatField(default=0)
    average_time_minutes = models.FloatField(default=0)
    score_distribution = models.JSONField(default=dict)
    question_difficulty_stats = models.JSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'assessment_analytics'


class ClassPerformanceSnapshot(models.Model):
    """Weekly snapshot of class performance."""
    school_class = models.ForeignKey('classes.SchoolClass', on_delete=models.CASCADE, related_name='snapshots')
    subject = models.ForeignKey('subjects.Subject', on_delete=models.CASCADE, related_name='class_snapshots')
    week_start = models.DateField()
    average_score = models.FloatField(default=0)
    participation_rate = models.FloatField(default=0)
    top_topic = models.CharField(max_length=255, blank=True)
    weak_topic = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'class_performance_snapshots'
        unique_together = ('school_class', 'subject', 'week_start')
        ordering = ['-week_start']
