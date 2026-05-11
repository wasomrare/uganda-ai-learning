"""Leaderboard models."""
from django.db import models


LEADERBOARD_TYPE_CHOICES = [
    ('overall', 'Overall School'),
    ('class', 'Class'),
    ('subject', 'Subject'),
    ('weekly', 'Weekly'),
    ('monthly', 'Monthly'),
    ('holiday', 'Holiday'),
]


class Leaderboard(models.Model):
    leaderboard_type = models.CharField(max_length=20, choices=LEADERBOARD_TYPE_CHOICES)
    school_class = models.ForeignKey('classes.SchoolClass', null=True, blank=True, on_delete=models.CASCADE)
    subject = models.ForeignKey('subjects.Subject', null=True, blank=True, on_delete=models.CASCADE)
    period_start = models.DateField()
    period_end = models.DateField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'leaderboards'


class LeaderboardEntry(models.Model):
    leaderboard = models.ForeignKey(Leaderboard, on_delete=models.CASCADE, related_name='entries')
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE)
    rank = models.PositiveIntegerField()
    score = models.FloatField(default=0)
    xp = models.PositiveIntegerField(default=0)
    assessments_completed = models.PositiveIntegerField(default=0)
    accuracy = models.FloatField(default=0)
    streak = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'leaderboard_entries'
        ordering = ['rank']
        unique_together = ('leaderboard', 'student')
