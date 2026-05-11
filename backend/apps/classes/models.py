"""School class / grade models."""
from django.db import models
from core.models import BaseModel


LEVEL_CHOICES = [
    ('P1', 'Primary 1'), ('P2', 'Primary 2'), ('P3', 'Primary 3'),
    ('P4', 'Primary 4'), ('P5', 'Primary 5'), ('P6', 'Primary 6'),
    ('P7', 'Primary 7'),
]


class SchoolClass(BaseModel):
    """Represents a primary school class (P1–P7)."""
    name = models.CharField(max_length=20, db_index=True)
    level = models.CharField(max_length=5, choices=LEVEL_CHOICES, db_index=True)
    stream = models.CharField(max_length=10, blank=True, help_text='e.g., A, B, Blue, Red')
    academic_year = models.PositiveIntegerField()
    term = models.PositiveIntegerField(choices=[(1, 'Term 1'), (2, 'Term 2'), (3, 'Term 3')], default=1)
    class_teacher = models.ForeignKey(
        'teachers.Teacher', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='class_teacher_of',
    )
    capacity = models.PositiveIntegerField(default=40)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'school_classes'
        unique_together = ('level', 'stream', 'academic_year')
        ordering = ['level', 'stream']

    def __str__(self):
        name = f'{self.level}'
        if self.stream:
            name += f' {self.stream}'
        return name

    @property
    def student_count(self):
        return self.students.filter(is_active=True).count()

    @property
    def is_lower_primary(self):
        return self.level in ('P1', 'P2', 'P3')

    @property
    def is_upper_primary(self):
        return self.level in ('P4', 'P5', 'P6', 'P7')
