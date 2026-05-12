"""Main URL configuration for Uganda Primary AI Learning System."""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView


def health_check(request):
    from django.db import connection
    status = {'db': False, 'admin_exists': False, 'user_count': 0}
    try:
        with connection.cursor() as c:
            c.execute('SELECT 1')
        status['db'] = True
        from apps.users.models import User
        status['user_count'] = User.objects.count()
        status['admin_exists'] = User.objects.filter(role='super_admin').exists()
    except Exception as e:
        status['error'] = str(e)
    return JsonResponse(status)

API_V1 = 'api/v1/'

urlpatterns = [
    path('admin/', admin.site.urls),
    path(f'{API_V1}health/', health_check, name='health'),

    # API Schema & Documentation
    path(f'{API_V1}schema/', SpectacularAPIView.as_view(), name='schema'),
    path(f'{API_V1}docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path(f'{API_V1}redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Authentication
    path(f'{API_V1}auth/', include('apps.authentication.urls')),

    # Users & Roles
    path(f'{API_V1}users/', include('apps.users.urls')),
    path(f'{API_V1}students/', include('apps.students.urls')),
    path(f'{API_V1}teachers/', include('apps.teachers.urls')),

    # Curriculum
    path(f'{API_V1}classes/', include('apps.classes.urls')),
    path(f'{API_V1}subjects/', include('apps.subjects.urls')),
    path(f'{API_V1}curriculum/', include('apps.curriculum.urls')),

    # Question Bank & Assessments
    path(f'{API_V1}questions/', include('apps.question_bank.urls')),
    path(f'{API_V1}assessments/', include('apps.assessments.urls')),

    # AI Engine
    path(f'{API_V1}ai/', include('apps.ai_engine.urls')),

    # Learning
    path(f'{API_V1}revision/', include('apps.revision.urls')),
    path(f'{API_V1}holidays/', include('apps.holidays.urls')),
    path(f'{API_V1}recommendations/', include('apps.recommendations.urls')),

    # Analytics & Performance
    path(f'{API_V1}analytics/', include('apps.analytics.urls')),
    path(f'{API_V1}performance/', include('apps.performance.urls')),

    # Gamification & Leaderboards
    path(f'{API_V1}gamification/', include('apps.gamification.urls')),
    path(f'{API_V1}leaderboards/', include('apps.leaderboards.urls')),

    # Communication
    path(f'{API_V1}notifications/', include('apps.notifications.urls')),
    path(f'{API_V1}chat/', include('apps.chat.urls')),

    # Live Classes
    path(f'{API_V1}live-classes/', include('apps.live_classes.urls')),

    # Reports & Uploads
    path(f'{API_V1}reports/', include('apps.reports.urls')),
    path(f'{API_V1}uploads/', include('apps.uploads.urls')),

    # Offline Sync
    path(f'{API_V1}sync/', include('apps.offline_sync.urls')),

    # Parent Portal
    path(f'{API_V1}parent/', include('apps.parent_portal.urls')),

    # Dashboard
    path(f'{API_V1}dashboard/', include('apps.dashboard.urls')),

    # Audit Logs
    path(f'{API_V1}audit/', include('apps.audit_logs.urls')),

    # System Settings
    path(f'{API_V1}settings/', include('apps.settings_app.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = 'Uganda Primary AI Learning — Admin'
admin.site.site_title = 'Uganda Learning Admin'
admin.site.index_title = 'System Administration'
