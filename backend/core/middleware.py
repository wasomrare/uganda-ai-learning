"""Custom middleware for request logging, audit trails, and security."""
import logging
import time
import json
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    """Logs all API requests with timing information."""

    EXCLUDED_PATHS = ['/health/', '/static/', '/media/']

    def process_request(self, request):
        request._start_time = time.time()

    def process_response(self, request, response):
        if any(request.path.startswith(p) for p in self.EXCLUDED_PATHS):
            return response

        duration_ms = round((time.time() - getattr(request, '_start_time', time.time())) * 1000, 2)
        user_id = request.user.id if hasattr(request, 'user') and request.user.is_authenticated else 'anon'

        logger.info(
            '[API] %s %s | status=%s | user=%s | time=%sms',
            request.method,
            request.path,
            response.status_code,
            user_id,
            duration_ms,
        )
        return response


class AuditLogMiddleware(MiddlewareMixin):
    """Creates audit log entries for write operations."""

    AUDIT_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']
    EXCLUDED_PATHS = ['/api/v1/auth/token/', '/api/v1/auth/token/refresh/', '/static/', '/media/']

    def process_response(self, request, response):
        if request.method not in self.AUDIT_METHODS:
            return response
        if any(request.path.startswith(p) for p in self.EXCLUDED_PATHS):
            return response
        if not (hasattr(request, 'user') and request.user.is_authenticated):
            return response
        if response.status_code >= 400:
            return response

        try:
            from apps.audit_logs.models import AuditLog
            AuditLog.objects.create(
                user=request.user,
                action=request.method,
                path=request.path[:255],
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
                status_code=response.status_code,
                timestamp=timezone.now(),
            )
        except Exception:
            pass

        return response

    @staticmethod
    def _get_client_ip(request):
        x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded:
            return x_forwarded.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')


class DeviceTrackingMiddleware(MiddlewareMixin):
    """Tracks device information for authenticated users."""

    def process_response(self, request, response):
        if not (hasattr(request, 'user') and request.user.is_authenticated):
            return response

        device_id = request.META.get('HTTP_X_DEVICE_ID')
        app_version = request.META.get('HTTP_X_APP_VERSION')

        if device_id and request.method in ('GET', 'POST'):
            try:
                from apps.authentication.models import UserDevice
                UserDevice.objects.update_or_create(
                    user=request.user,
                    device_id=device_id,
                    defaults={
                        'app_version': app_version or '',
                        'user_agent': request.META.get('HTTP_USER_AGENT', '')[:255],
                        'ip_address': self._get_client_ip(request),
                        'last_seen': timezone.now(),
                    }
                )
            except Exception:
                pass

        return response

    @staticmethod
    def _get_client_ip(request):
        x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded:
            return x_forwarded.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')
