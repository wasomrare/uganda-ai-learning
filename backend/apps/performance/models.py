"""Performance tracking models."""
from django.db import models


class PLEReadinessScore(models.Model):
    """PLE readiness prediction for P7 students."""
    student = models.OneToOneField('students.Student', on_delete=models.CASCADE, related_name='ple_readiness')
    overall_score = models.FloatField(default=0)
    english_score = models.FloatField(default=0)
    mathematics_score = models.FloatField(default=0)
    science_score = models.FloatField(default=0)
    sst_score = models.FloatField(default=0)
    predicted_aggregate = models.CharField(max_length=10, blank=True)
    confidence_level = models.FloatField(default=0)
    ai_analysis = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ple_readiness_scores'

    def __str__(self):
        return f'PLE Readiness: {self.student.full_name} — {self.predicted_aggregate}'
