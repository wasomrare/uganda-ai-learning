"""Subject models aligned to Ugandan UNEB primary curriculum."""
from django.db import models
from core.models import BaseModel


class Subject(BaseModel):
    """A school subject taught in Ugandan primary schools."""

    CATEGORY_CHOICES = [
        ('core', 'Core Subject'),
        ('language', 'Language'),
        ('stem', 'STEM'),
        ('social', 'Social Studies'),
        ('religious', 'Religious Education'),
        ('practical', 'Practical'),
    ]

    name = models.CharField(max_length=100, db_index=True)
    code = models.CharField(max_length=20, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='core')
    class_levels = models.JSONField(
        default=list,
        help_text='List of class levels e.g. ["P1","P2","P3"]',
    )
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=100, blank=True, help_text='Emoji or icon name')
    color = models.CharField(max_length=20, blank=True, help_text='Hex color for UI')
    is_examinable = models.BooleanField(default=True, help_text='Appears in PLE/exams')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text='Display order')

    class Meta:
        db_table = 'subjects'
        ordering = ['order', 'name']

    def __str__(self):
        return f'{self.name} ({self.code})'

    @property
    def is_lower_primary_subject(self):
        lower = {'P1', 'P2', 'P3'}
        return bool(lower.intersection(set(self.class_levels)))

    @property
    def is_upper_primary_subject(self):
        upper = {'P4', 'P5', 'P6', 'P7'}
        return bool(upper.intersection(set(self.class_levels)))
