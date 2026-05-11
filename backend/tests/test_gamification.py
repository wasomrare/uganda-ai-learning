"""Gamification unit tests."""
import pytest


@pytest.mark.django_db
class TestXPSystem:
    def test_xp_award_increases_total(self, student_profile):
        from apps.gamification.models import StudentXP, award_xp
        award_xp(student_profile, 100, 'test')
        xp = StudentXP.objects.get(student=student_profile)
        assert xp.total_xp == 100

    def test_level_up_at_500_xp(self, student_profile):
        from apps.gamification.models import StudentXP, award_xp
        award_xp(student_profile, 500, 'test')
        xp = StudentXP.objects.get(student=student_profile)
        assert xp.level == 2

    def test_multiple_xp_awards_accumulate(self, student_profile):
        from apps.gamification.models import StudentXP, award_xp
        award_xp(student_profile, 50, 'revision')
        award_xp(student_profile, 75, 'quiz')
        xp = StudentXP.objects.get(student=student_profile)
        assert xp.total_xp == 125

    def test_xp_transaction_logged(self, student_profile):
        from apps.gamification.models import StudentXP, XPTransaction, award_xp
        award_xp(student_profile, 30, 'daily_login')
        xp = StudentXP.objects.get(student=student_profile)
        assert xp.transactions.filter(reason='daily_login').exists()


@pytest.mark.django_db
class TestStreakSystem:
    def test_first_activity_starts_streak(self, student_profile):
        from apps.gamification.models import Streak
        streak, _ = Streak.objects.get_or_create(student=student_profile)
        streak.update_streak()
        assert streak.current_streak == 1

    def test_same_day_does_not_increase_streak(self, student_profile):
        from apps.gamification.models import Streak
        streak, _ = Streak.objects.get_or_create(student=student_profile)
        streak.update_streak()
        streak.update_streak()
        assert streak.current_streak == 1

    def test_consecutive_days_build_streak(self, student_profile):
        from apps.gamification.models import Streak
        from datetime import date, timedelta
        streak, _ = Streak.objects.get_or_create(student=student_profile)
        streak.last_activity_date = date.today() - timedelta(days=1)
        streak.current_streak = 3
        streak.save()
        streak.update_streak()
        assert streak.current_streak == 4
