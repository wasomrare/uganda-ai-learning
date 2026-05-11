"""Holiday learning background tasks."""
try:
    from celery import shared_task
except ImportError:
    def shared_task(*args, **kwargs):
        def decorator(func): return func
        return decorator if args and callable(args[0]) else decorator
import logging

logger = logging.getLogger(__name__)


@shared_task(name='apps.holidays.tasks.generate_holiday_daily_tasks')
def generate_holiday_daily_tasks():
    """Generate today's tasks for all active holiday packages."""
    from .models import HolidayPackage, StudentHolidayProgress
    from apps.students.models import Student
    from django.utils import timezone

    today = timezone.now().date()
    active_packages = HolidayPackage.objects.filter(
        is_active=True, start_date__lte=today, end_date__gte=today
    )

    for package in active_packages:
        students = Student.objects.filter(
            current_class__level=package.class_level, is_active=True
        )
        for student in students:
            StudentHolidayProgress.objects.get_or_create(
                student=student, package=package
            )

    return {'packages_processed': active_packages.count()}
