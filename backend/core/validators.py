"""Custom Django validators."""
import os
from django.core.exceptions import ValidationError
from django.conf import settings


def validate_file_size(file):
    """Validate uploaded file does not exceed max size."""
    max_size = getattr(settings, 'MAX_FILE_UPLOAD_SIZE', 10 * 1024 * 1024)
    if file.size > max_size:
        raise ValidationError(
            f'File size {file.size / (1024*1024):.1f}MB exceeds maximum allowed size of '
            f'{max_size / (1024*1024):.0f}MB.'
        )


def validate_file_extension(file):
    """Validate file extension is allowed."""
    allowed = getattr(settings, 'ALLOWED_UPLOAD_EXTENSIONS', [])
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in allowed:
        raise ValidationError(
            f'File type "{ext}" is not allowed. Allowed types: {", ".join(allowed)}'
        )


def validate_ugandan_phone(value):
    """Validate Ugandan phone number format."""
    import re
    pattern = r'^(\+256|0)[0-9]{9}$'
    if not re.match(pattern, str(value)):
        raise ValidationError(
            'Enter a valid Ugandan phone number (e.g., +256700123456 or 0700123456).'
        )


def validate_class_level(value):
    """Validate Ugandan primary class level."""
    valid = ['P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7']
    if value not in valid:
        raise ValidationError(f'Class must be one of: {", ".join(valid)}')


def validate_term(value):
    """Validate school term (1, 2, or 3)."""
    if value not in (1, 2, 3):
        raise ValidationError('Term must be 1, 2, or 3.')


def validate_score(value):
    """Validate score is between 0 and 100."""
    if not (0 <= value <= 100):
        raise ValidationError('Score must be between 0 and 100.')
