"""Custom exception handling."""
import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from rest_framework.exceptions import (
    ValidationError, AuthenticationFailed, NotAuthenticated,
    PermissionDenied, NotFound, Throttled,
)

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """Unified JSON error response format."""

    if isinstance(exc, DjangoValidationError):
        exc = ValidationError(detail=exc.message_dict if hasattr(exc, 'message_dict') else exc.messages)

    if isinstance(exc, Http404):
        exc = NotFound()

    response = exception_handler(exc, context)

    if response is not None:
        error_data = {
            'status': 'error',
            'code': response.status_code,
            'message': _get_error_message(exc),
            'errors': response.data,
        }

        if response.status_code == 401:
            error_data['message'] = 'Authentication required. Please log in.'
        elif response.status_code == 403:
            error_data['message'] = 'You do not have permission to perform this action.'
        elif response.status_code == 404:
            error_data['message'] = 'The requested resource was not found.'
        elif response.status_code == 429:
            error_data['message'] = 'Too many requests. Please slow down.'

        response.data = error_data
        return response

    logger.exception('Unhandled exception in API view', exc_info=exc)
    return Response({
        'status': 'error',
        'code': 500,
        'message': 'An unexpected error occurred. Please try again later.',
        'errors': {},
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _get_error_message(exc):
    if isinstance(exc, ValidationError):
        return 'Validation failed. Please check your input.'
    if isinstance(exc, (AuthenticationFailed, NotAuthenticated)):
        return 'Authentication failed.'
    if isinstance(exc, PermissionDenied):
        return str(exc.detail) if exc.detail else 'Permission denied.'
    if isinstance(exc, NotFound):
        return 'Resource not found.'
    if isinstance(exc, Throttled):
        return f'Request throttled. Retry after {exc.wait:.0f} seconds.'
    return 'An error occurred.'


class AppError(Exception):
    """Base application error."""
    def __init__(self, message, code=None, status_code=400):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class AIServiceError(AppError):
    """Raised when AI service fails."""
    def __init__(self, message='AI service unavailable', provider=None):
        self.provider = provider
        super().__init__(message, code='AI_SERVICE_ERROR', status_code=503)


class QuotaExceededError(AppError):
    """Raised when AI API quota is exceeded."""
    def __init__(self, provider=None):
        super().__init__(
            f'AI quota exceeded for provider: {provider}',
            code='QUOTA_EXCEEDED',
            status_code=429,
        )


class AccountLockedError(AppError):
    """Raised when account is locked."""
    def __init__(self):
        super().__init__('Account is locked due to multiple failed attempts.', code='ACCOUNT_LOCKED', status_code=403)
