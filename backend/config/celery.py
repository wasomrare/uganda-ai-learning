"""Celery configuration for Uganda Primary AI Learning System."""
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('uganda_learning')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# ============================================================
# PERIODIC TASKS (Beat Schedule)
# ============================================================
app.conf.beat_schedule = {
    'generate-daily-revision-questions': {
        'task': 'apps.ai_engine.tasks.generate_daily_revision_batch',
        'schedule': crontab(hour=5, minute=0),
    },
    'generate-weekly-assessments': {
        'task': 'apps.ai_engine.tasks.generate_weekly_assessments',
        'schedule': crontab(day_of_week='monday', hour=6, minute=0),
    },
    'process-analytics': {
        'task': 'apps.analytics.tasks.process_daily_analytics',
        'schedule': crontab(hour=23, minute=30),
    },
    'send-revision-reminders': {
        'task': 'apps.notifications.tasks.send_revision_reminders',
        'schedule': crontab(hour=16, minute=0),
    },
    'update-leaderboards': {
        'task': 'apps.leaderboards.tasks.update_all_leaderboards',
        'schedule': crontab(hour='*/2', minute=0),
    },
    'calculate-mastery-scores': {
        'task': 'apps.performance.tasks.calculate_mastery_scores',
        'schedule': crontab(hour=3, minute=0),
    },
    'holiday-daily-tasks': {
        'task': 'apps.holidays.tasks.generate_holiday_daily_tasks',
        'schedule': crontab(hour=6, minute=30),
    },
    'cleanup-expired-tokens': {
        'task': 'apps.authentication.tasks.cleanup_expired_tokens',
        'schedule': crontab(hour=2, minute=0),
    },
    'sync-offline-queues': {
        'task': 'apps.offline_sync.tasks.process_sync_queue',
        'schedule': crontab(minute='*/15'),
    },
    'detect-struggling-learners': {
        'task': 'apps.recommendations.tasks.detect_struggling_learners',
        'schedule': crontab(hour=7, minute=0),
    },
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
