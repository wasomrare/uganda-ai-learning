"""Curriculum models — topics, subtopics, competencies, learning objectives."""
from django.db import models
from core.models import BaseModel


DIFFICULTY_CHOICES = [
    ('beginner', 'Beginner'),
    ('easy', 'Easy'),
    ('medium', 'Medium'),
    ('hard', 'Hard'),
    ('advanced', 'Advanced'),
]

TERM_CHOICES = [(1, 'Term 1'), (2, 'Term 2'), (3, 'Term 3')]


class Topic(BaseModel):
    """A curriculum topic within a subject and class level."""
    subject = models.ForeignKey('subjects.Subject', on_delete=models.CASCADE, related_name='topics')
    class_level = models.CharField(max_length=5, db_index=True)
    term = models.PositiveIntegerField(choices=TERM_CHOICES)
    week = models.PositiveIntegerField(default=1, help_text='Week in the term')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    learning_objectives = models.JSONField(default=list)
    competencies = models.JSONField(default=list)
    key_vocabulary = models.JSONField(default=list)
    difficulty = models.CharField(max_length=15, choices=DIFFICULTY_CHOICES, default='medium')
    estimated_mastery_hours = models.FloatField(default=1.0)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    ai_generation_prompt_hint = models.TextField(
        blank=True,
        help_text='Hint for AI question generation specific to this topic',
    )

    class Meta:
        db_table = 'curriculum_topics'
        ordering = ['class_level', 'term', 'week', 'order']
        indexes = [
            models.Index(fields=['subject', 'class_level', 'term']),
            models.Index(fields=['class_level', 'term', 'week']),
        ]

    def __str__(self):
        return f'{self.class_level} | {self.subject.name} | T{self.term}W{self.week} | {self.name}'


class SubTopic(BaseModel):
    """Granular subtopic under a topic."""
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='subtopics')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    learning_outcomes = models.JSONField(default=list)
    difficulty = models.CharField(max_length=15, choices=DIFFICULTY_CHOICES, default='medium')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'curriculum_subtopics'
        ordering = ['order']

    def __str__(self):
        return f'{self.topic.name} > {self.name}'


class LearningResource(BaseModel):
    """A learning resource (PDF, video, audio) linked to a topic."""
    RESOURCE_TYPES = [
        ('pdf', 'PDF Document'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('image', 'Image'),
        ('link', 'External Link'),
        ('text', 'Text Content'),
    ]

    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=255)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    file = models.FileField(upload_to='curriculum/resources/', null=True, blank=True)
    url = models.URLField(blank=True)
    content = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(
        'users.User', null=True, on_delete=models.SET_NULL, related_name='uploaded_resources',
    )
    is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    download_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'curriculum_resources'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} ({self.resource_type})'
