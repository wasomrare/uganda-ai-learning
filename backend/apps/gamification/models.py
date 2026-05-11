"""Gamification models — XP, levels, badges, streaks, achievements."""
from django.db import models
from core.models import BaseModel


class Badge(BaseModel):
    """Defines a badge/achievement that can be earned."""
    CATEGORY_CHOICES = [
        ('academic', 'Academic Excellence'),
        ('streak', 'Learning Streak'),
        ('subject', 'Subject Master'),
        ('speed', 'Speed'),
        ('consistency', 'Consistency'),
        ('holiday', 'Holiday Champion'),
        ('helper', 'Helper'),
        ('special', 'Special'),
    ]

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    icon = models.CharField(max_length=100)
    color = models.CharField(max_length=20, default='#6366f1')
    image = models.ImageField(upload_to='badges/', null=True, blank=True)
    xp_reward = models.PositiveIntegerField(default=50)
    coin_reward = models.PositiveIntegerField(default=10)
    requirement_type = models.CharField(max_length=50)
    requirement_value = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    rarity = models.CharField(
        max_length=20,
        choices=[('common', 'Common'), ('rare', 'Rare'), ('epic', 'Epic'), ('legendary', 'Legendary')],
        default='common',
    )

    class Meta:
        db_table = 'badges'
        ordering = ['category', 'name']

    def __str__(self):
        return f'{self.name} ({self.category})'


class StudentBadge(BaseModel):
    """Badge earned by a student."""
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='earned_badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='earners')
    earned_at = models.DateTimeField(auto_now_add=True)
    context = models.JSONField(default=dict)

    class Meta:
        db_table = 'student_badges'
        unique_together = ('student', 'badge')
        ordering = ['-earned_at']

    def __str__(self):
        return f'{self.student.full_name} — {self.badge.name}'


class StudentXP(models.Model):
    """XP (experience points) tracking for a student."""
    student = models.OneToOneField('students.Student', on_delete=models.CASCADE, related_name='xp')
    total_xp = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)
    coins = models.PositiveIntegerField(default=0)
    weekly_xp = models.PositiveIntegerField(default=0)
    monthly_xp = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'student_xp'

    def __str__(self):
        return f'{self.student.full_name} — Level {self.level} ({self.total_xp} XP)'

    @property
    def xp_for_next_level(self):
        return self.level * 500

    @property
    def xp_progress(self):
        base = (self.level - 1) * 500
        current = self.total_xp - base
        needed = self.xp_for_next_level
        return round((current / needed) * 100, 1) if needed else 100

    def add_xp(self, amount: int, reason: str = ''):
        self.total_xp += amount
        self.weekly_xp += amount
        self.monthly_xp += amount
        new_level = (self.total_xp // 500) + 1
        leveled_up = new_level > self.level
        self.level = new_level
        self.save()
        XPTransaction.objects.create(student_xp=self, amount=amount, reason=reason)
        return leveled_up


class XPTransaction(models.Model):
    """Log of XP earned/spent."""
    student_xp = models.ForeignKey(StudentXP, on_delete=models.CASCADE, related_name='transactions')
    amount = models.IntegerField()
    reason = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'xp_transactions'
        ordering = ['-timestamp']


class Streak(models.Model):
    """Daily learning streak tracking."""
    student = models.OneToOneField('students.Student', on_delete=models.CASCADE, related_name='streak')
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)
    total_active_days = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'streaks'

    def update_streak(self):
        from django.utils import timezone
        today = timezone.now().date()
        if self.last_activity_date == today:
            return False
        if self.last_activity_date and (today - self.last_activity_date).days == 1:
            self.current_streak += 1
        else:
            self.current_streak = 1
        self.last_activity_date = today
        self.total_active_days += 1
        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak
        self.save()
        return True


def award_xp(student, amount: int, reason: str = ''):
    """Helper to award XP and check for badge unlocks."""
    xp_obj, _ = StudentXP.objects.get_or_create(student=student)
    leveled_up = xp_obj.add_xp(amount, reason)

    ai_profile = getattr(student, 'ai_profile', None)
    if ai_profile:
        ai_profile.current_streak = getattr(getattr(student, 'streak', None), 'current_streak', 0)
        ai_profile.save(update_fields=['current_streak'])

    return leveled_up
