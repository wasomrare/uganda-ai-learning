"""Student profile and learning profile models."""
import uuid
from django.db import models
from core.models import BaseModel


class Student(BaseModel):
    """Student profile linked to a User account."""

    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='student_profile')
    admission_number = models.CharField(max_length=50, unique=True, db_index=True)
    current_class = models.ForeignKey(
        'classes.SchoolClass', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='students',
    )
    stream = models.CharField(max_length=10, blank=True)
    enrollment_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=10,
        choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
        blank=True,
    )
    religion = models.CharField(max_length=50, blank=True)
    previous_school = models.CharField(max_length=255, blank=True)
    special_needs = models.TextField(blank=True)

    photo = models.ImageField(upload_to='students/photos/', null=True, blank=True)

    class Meta:
        db_table = 'students'
        ordering = ['current_class', 'user__last_name']
        indexes = [
            models.Index(fields=['current_class', 'is_active']),
            models.Index(fields=['admission_number']),
        ]

    def __str__(self):
        return f'{self.user.get_full_name()} ({self.admission_number})'

    @property
    def full_name(self):
        return self.user.get_full_name()

    @property
    def class_name(self):
        return self.current_class.name if self.current_class else 'Unassigned'


class ParentGuardian(BaseModel):
    """Parent or guardian information linked to a student."""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='parents')
    full_name = models.CharField(max_length=200)
    relationship = models.CharField(
        max_length=30,
        choices=[
            ('father', 'Father'), ('mother', 'Mother'), ('guardian', 'Guardian'),
            ('uncle', 'Uncle'), ('aunt', 'Aunt'), ('other', 'Other'),
        ],
    )
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    occupation = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    is_primary = models.BooleanField(default=False)
    user = models.ForeignKey(
        'users.User', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='children',
    )

    class Meta:
        db_table = 'parent_guardians'

    def __str__(self):
        return f'{self.full_name} ({self.relationship} of {self.student.full_name})'


class StudentAIProfile(models.Model):
    """AI-tracked learning profile for adaptive learning."""
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='ai_profile')

    overall_mastery = models.FloatField(default=0.0)
    learning_speed = models.CharField(
        max_length=20,
        choices=[('slow', 'Slow'), ('average', 'Average'), ('fast', 'Fast')],
        default='average',
    )
    preferred_difficulty = models.CharField(
        max_length=20,
        choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')],
        default='medium',
    )
    strong_subjects = models.JSONField(default=list)
    weak_subjects = models.JSONField(default=list)
    strong_topics = models.JSONField(default=list)
    weak_topics = models.JSONField(default=list)
    learning_style = models.CharField(max_length=50, blank=True)
    ai_notes = models.TextField(blank=True)

    total_questions_attempted = models.IntegerField(default=0)
    total_correct = models.IntegerField(default=0)
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_activity = models.DateTimeField(null=True, blank=True)
    ple_readiness_score = models.FloatField(default=0.0)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'student_ai_profiles'

    def __str__(self):
        return f'AI Profile: {self.student.full_name}'

    @property
    def accuracy_rate(self):
        if not self.total_questions_attempted:
            return 0.0
        return round((self.total_correct / self.total_questions_attempted) * 100, 2)
