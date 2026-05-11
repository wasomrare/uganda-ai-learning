"""Question bank models — all question types for Uganda primary curriculum."""
from django.db import models
from core.models import BaseModel


QUESTION_TYPE_CHOICES = [
    ('mcq', 'Multiple Choice'),
    ('true_false', 'True / False'),
    ('fill_blank', 'Fill in the Blank'),
    ('short_answer', 'Short Answer'),
    ('matching', 'Matching'),
    ('composition', 'Composition / Essay'),
    ('comprehension', 'Comprehension'),
    ('spelling', 'Spelling'),
    ('drag_drop', 'Drag and Drop'),
    ('image_based', 'Image-Based'),
    ('audio_based', 'Audio-Based'),
    ('sentence_arrangement', 'Sentence Arrangement'),
    ('diagram_labeling', 'Diagram Labeling'),
]

DIFFICULTY_CHOICES = [
    ('easy', 'Easy'),
    ('medium', 'Medium'),
    ('hard', 'Hard'),
]

SOURCE_CHOICES = [
    ('ai_generated', 'AI Generated'),
    ('teacher_created', 'Teacher Created'),
    ('imported', 'Imported'),
    ('past_paper', 'Past Paper'),
]


class Question(BaseModel):
    """A single question in the question bank."""

    question_type = models.CharField(max_length=30, choices=QUESTION_TYPE_CHOICES, db_index=True)
    subject = models.ForeignKey('subjects.Subject', on_delete=models.CASCADE, related_name='questions')
    topic = models.ForeignKey(
        'curriculum.Topic', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='questions',
    )
    subtopic = models.ForeignKey(
        'curriculum.SubTopic', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='questions',
    )
    class_level = models.CharField(max_length=5, db_index=True)
    term = models.PositiveIntegerField(choices=[(1, 'Term 1'), (2, 'Term 2'), (3, 'Term 3')], null=True, blank=True)

    question_text = models.TextField()
    question_image = models.ImageField(upload_to='questions/images/', null=True, blank=True)
    question_audio = models.FileField(upload_to='questions/audio/', null=True, blank=True)
    question_html = models.TextField(blank=True, help_text='Rich HTML version for web rendering')

    marks = models.FloatField(default=1.0)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium', db_index=True)
    estimated_time_seconds = models.PositiveIntegerField(default=60)

    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='ai_generated', db_index=True)
    created_by = models.ForeignKey(
        'users.User', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='created_questions',
    )
    ai_model_used = models.CharField(max_length=100, blank=True)
    ai_prompt_hash = models.CharField(max_length=64, blank=True, db_index=True)

    is_approved = models.BooleanField(default=False, db_index=True)
    is_active = models.BooleanField(default=True)
    use_count = models.PositiveIntegerField(default=0)
    correct_rate = models.FloatField(default=0.0, help_text='Percentage of correct answers historically')

    tags = models.JSONField(default=list)
    learning_objectives = models.JSONField(default=list)
    adaptive_tags = models.JSONField(default=dict)

    class Meta:
        db_table = 'question_bank'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['subject', 'class_level', 'difficulty']),
            models.Index(fields=['question_type', 'is_approved', 'is_active']),
            models.Index(fields=['topic', 'class_level']),
        ]

    def __str__(self):
        return f'[{self.question_type}] {self.question_text[:80]}'


class MCQOption(models.Model):
    """Options for multiple choice questions."""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    option_label = models.CharField(max_length=5)
    option_text = models.TextField()
    option_image = models.ImageField(upload_to='questions/options/', null=True, blank=True)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'mcq_options'
        ordering = ['order']

    def __str__(self):
        return f'{self.option_label}. {self.option_text[:50]}'


class QuestionAnswer(models.Model):
    """Model answer / answer key for a question."""
    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name='answer')
    answer_text = models.TextField()
    answer_keywords = models.JSONField(default=list, help_text='Keywords for AI marking')
    explanation = models.TextField(blank=True, help_text='AI-generated explanation')
    hints = models.JSONField(default=list)
    marking_guide = models.TextField(blank=True)
    marking_rubric = models.JSONField(default=dict, help_text='Rubric for composition/essay marking')
    minimum_keywords_required = models.PositiveIntegerField(default=1)
    case_sensitive = models.BooleanField(default=False)

    class Meta:
        db_table = 'question_answers'

    def __str__(self):
        return f'Answer for: {self.question.question_text[:50]}'


class MatchingPair(models.Model):
    """Pairs for matching questions."""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='matching_pairs')
    left_text = models.CharField(max_length=255)
    right_text = models.CharField(max_length=255)
    left_image = models.ImageField(upload_to='questions/matching/', null=True, blank=True)
    right_image = models.ImageField(upload_to='questions/matching/', null=True, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'matching_pairs'
        ordering = ['order']


class FillBlankSegment(models.Model):
    """Text segments for fill-in-the-blank questions."""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='segments')
    segment_text = models.TextField()
    is_blank = models.BooleanField(default=False)
    blank_answer = models.CharField(max_length=255, blank=True)
    accepted_answers = models.JSONField(default=list)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'fill_blank_segments'
        ordering = ['order']
