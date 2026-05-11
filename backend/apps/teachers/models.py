"""Teacher profile models."""
import uuid
from django.db import models
from core.models import BaseModel


class Teacher(BaseModel):
    """Teacher profile linked to a User account."""
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='teacher_profile')
    employee_number = models.CharField(max_length=50, unique=True, db_index=True)
    qualification = models.CharField(max_length=255, blank=True)
    specialization = models.CharField(max_length=255, blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    is_class_teacher = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    classes = models.ManyToManyField('classes.SchoolClass', blank=True, related_name='teachers')
    subjects = models.ManyToManyField('subjects.Subject', blank=True, related_name='teachers')

    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='teachers/photos/', null=True, blank=True)

    can_generate_ai_content = models.BooleanField(default=True)
    can_override_ai_marks = models.BooleanField(default=True)
    can_publish_results = models.BooleanField(default=False)

    class Meta:
        db_table = 'teachers'
        ordering = ['user__last_name']

    def __str__(self):
        return f'{self.user.get_full_name()} ({self.employee_number})'

    @property
    def full_name(self):
        return self.user.get_full_name()
