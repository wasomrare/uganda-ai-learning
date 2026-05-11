"""Shared utility functions."""
import re
import hashlib
import secrets
import string
from django.utils import timezone
from django.http import JsonResponse


def axes_lockout_handler(request, credentials, *args, **kwargs):
    """Custom handler for axes account lockout."""
    return JsonResponse({
        'status': 'error',
        'code': 403,
        'message': 'Account locked due to too many failed login attempts. Please try again later.',
        'errors': {'non_field_errors': ['Account temporarily locked.']},
    }, status=403)


def generate_admission_number(class_name: str, year: int = None) -> str:
    """Generate unique student admission number."""
    if year is None:
        year = timezone.now().year
    random_part = secrets.token_hex(3).upper()
    return f'UG/{class_name}/{year}/{random_part}'


def generate_secure_password(length: int = 12) -> str:
    """Generate a secure random password."""
    alphabet = string.ascii_letters + string.digits + '!@#$%'
    while True:
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        if (
            any(c.islower() for c in password) and
            any(c.isupper() for c in password) and
            any(c.isdigit() for c in password)
        ):
            return password


def get_client_ip(request) -> str:
    """Extract client IP address from request."""
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


def calculate_percentage(score: float, total: float) -> float:
    """Calculate percentage score, handling division by zero."""
    if not total:
        return 0.0
    return round((score / total) * 100, 2)


def get_grade_and_comment(percentage: float) -> dict:
    """Return Ugandan primary school grade based on percentage."""
    if percentage >= 85:
        return {'grade': 'D1', 'comment': 'Excellent', 'color': '#22c55e'}
    elif percentage >= 75:
        return {'grade': 'D2', 'comment': 'Very Good', 'color': '#84cc16'}
    elif percentage >= 65:
        return {'grade': 'C3', 'comment': 'Good', 'color': '#eab308'}
    elif percentage >= 55:
        return {'grade': 'C4', 'comment': 'Fair', 'color': '#f97316'}
    elif percentage >= 45:
        return {'grade': 'C5', 'comment': 'Satisfactory', 'color': '#f97316'}
    elif percentage >= 40:
        return {'grade': 'C6', 'comment': 'Pass', 'color': '#ef4444'}
    elif percentage >= 35:
        return {'grade': 'P7', 'comment': 'Below Average', 'color': '#ef4444'}
    elif percentage >= 30:
        return {'grade': 'P8', 'comment': 'Poor', 'color': '#dc2626'}
    else:
        return {'grade': 'F9', 'comment': 'Fail', 'color': '#dc2626'}


def get_current_term() -> int:
    """Return current Uganda school term (1, 2, or 3) based on month."""
    month = timezone.now().month
    if 2 <= month <= 4:
        return 1
    elif 5 <= month <= 8:
        return 2
    elif 9 <= month <= 11:
        return 3
    return 1


def sanitize_text(text: str) -> str:
    """Remove potentially harmful HTML/script content."""
    clean = re.sub(r'<[^>]+>', '', text)
    clean = re.sub(r'javascript:', '', clean, flags=re.IGNORECASE)
    return clean.strip()


def chunk_list(lst: list, chunk_size: int) -> list:
    """Split list into chunks of given size."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def hash_content(content: str) -> str:
    """Hash content for duplicate detection."""
    return hashlib.sha256(content.encode()).hexdigest()


def get_mastery_level(score: float) -> dict:
    """Convert mastery score to level label."""
    if score >= 90:
        return {'level': 'mastered', 'label': 'Mastered', 'color': '#22c55e', 'icon': '🏆'}
    elif score >= 75:
        return {'level': 'proficient', 'label': 'Proficient', 'color': '#84cc16', 'icon': '⭐'}
    elif score >= 60:
        return {'level': 'developing', 'label': 'Developing', 'color': '#eab308', 'icon': '📈'}
    elif score >= 40:
        return {'level': 'emerging', 'label': 'Emerging', 'color': '#f97316', 'icon': '🌱'}
    else:
        return {'level': 'beginning', 'label': 'Needs Help', 'color': '#ef4444', 'icon': '🆘'}


def success_response(data, message='Success', status_code=200) -> dict:
    """Standard success response format."""
    return {
        'status': 'success',
        'message': message,
        'data': data,
    }
