"""Assessment models — exams, quizzes, tests, attempts, answers."""
from django.db import models
from core.models import BaseModel


ASSESSMENT_TYPE_CHOICES = [
    ('daily_revision', 'Daily Revision'),
    ('weekly_quiz', 'Weekly Quiz'),
    ('topic_test', 'Topic Test'),
    ('term_exam', 'Terminal Exam'),
    ('mock_exam', 'Mock Exam'),
    ('holiday_revision', 'Holiday Revision'),
    ('adaptive_test', 'Adaptive Test'),
    ('diagnostic', 'Diagnostic Test'),
    ('ple_practice', 'PLE Practice'),
]

STATUS_CHOICES = [
    ('draft', 'Draft'),
    ('ready', 'Ready'),
    ('active', 'Active / Live'),
    ('completed', 'Completed'),
    ('archived', 'Archived'),
]

ATTEMPT_STATUS_CHOICES = [
    ('in_progress', 'In Progress'),
    ('submitted', 'Submitted'),
    ('ai_marked', 'AI Marked'),
    ('teacher_reviewed', 'Teacher Reviewed'),
    ('published', 'Published'),
]


class Assessment(BaseModel):
    """An exam, quiz, or test."""
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    assessment_type = models.CharField(max_length=30, choices=ASSESSMENT_TYPE_CHOICES, db_index=True)
    school_class = models.ForeignKey('classes.SchoolClass', null=True, blank=True, on_delete=models.SET_NULL, related_name='assessments')
    class_level = models.CharField(max_length=5, db_index=True)
    subject = models.ForeignKey('subjects.Subject', null=True, blank=True, on_delete=models.SET_NULL, related_name='assessments')
    term = models.PositiveIntegerField(choices=[(1, 'Term 1'), (2, 'Term 2'), (3, 'Term 3')], default=1)
    academic_year = models.PositiveIntegerField()

    questions = models.ManyToManyField('question_bank.Question', through='AssessmentQuestion', blank=True)
    total_marks = models.FloatField(default=0)
    passing_marks = models.FloatField(default=0)
    duration_minutes = models.PositiveIntegerField(default=40)
    shuffle_questions = models.BooleanField(default=True)
    shuffle_options = models.BooleanField(default=True)
    show_results_immediately = models.BooleanField(default=True)
    allow_review = models.BooleanField(default=True)
    max_attempts = models.PositiveIntegerField(default=1)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', db_index=True)
    is_ai_generated = models.BooleanField(default=False)
    created_by = models.ForeignKey('users.User', null=True, blank=True, on_delete=models.SET_NULL, related_name='created_assessments')

    scheduled_start = models.DateTimeField(null=True, blank=True)
    scheduled_end = models.DateTimeField(null=True, blank=True)
    instructions = models.TextField(blank=True)
    anti_cheat_enabled = models.BooleanField(default=True)

    class Meta:
        db_table = 'assessments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['class_level', 'assessment_type', 'status']),
            models.Index(fields=['school_class', 'term']),
        ]

    def __str__(self):
        return f'{self.title} ({self.class_level})'


class AssessmentQuestion(models.Model):
    """Through model linking questions to assessments with ordering."""
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='assessment_questions')
    question = models.ForeignKey('question_bank.Question', on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)
    marks_override = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'assessment_questions'
        ordering = ['order']
        unique_together = ('assessment', 'question')


class AssessmentAttempt(BaseModel):
    """A student's attempt at an assessment."""
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='attempts')
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='attempts')
    attempt_number = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=ATTEMPT_STATUS_CHOICES, default='in_progress')

    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    time_taken_seconds = models.PositiveIntegerField(default=0)

    ai_score = models.FloatField(default=0)
    teacher_score = models.FloatField(null=True, blank=True)
    final_score = models.FloatField(default=0)
    percentage = models.FloatField(default=0)
    is_passed = models.BooleanField(default=False)

    teacher_comment = models.TextField(blank=True)
    ai_overall_feedback = models.TextField(blank=True)
    is_flagged = models.BooleanField(default=False, help_text='Flagged for suspicious activity')
    flag_reason = models.CharField(max_length=255, blank=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    device_id = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'assessment_attempts'
        unique_together = ('assessment', 'student', 'attempt_number')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.student.full_name} — {self.assessment.title}'


class StudentAnswer(BaseModel):
    """A student's answer to a single question in an attempt."""
    attempt = models.ForeignKey(AssessmentAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey('question_bank.Question', on_delete=models.CASCADE)

    selected_option = models.ForeignKey(
        'question_bank.MCQOption', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='selected_answers',
    )
    text_answer = models.TextField(blank=True)
    matching_answer = models.JSONField(default=dict)
    drag_drop_answer = models.JSONField(default=list)
    arrangement_answer = models.JSONField(default=list)
    selected_labels = models.JSONField(default=list, help_text='For diagram labeling')

    ai_score = models.FloatField(default=0)
    ai_feedback = models.TextField(blank=True)
    ai_confidence = models.FloatField(default=0)
    teacher_score = models.FloatField(null=True, blank=True)
    teacher_comment = models.TextField(blank=True)
    is_correct = models.BooleanField(null=True, blank=True)
    final_score = models.FloatField(default=0)

    time_taken_seconds = models.PositiveIntegerField(default=0)
    hint_used = models.BooleanField(default=False)

    class Meta:
        db_table = 'student_answers'
        unique_together = ('attempt', 'question')
