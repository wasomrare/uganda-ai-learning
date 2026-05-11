from django.urls import path
from .views import PLEReadinessView

urlpatterns = [
    path('ple/<uuid:student_id>/', PLEReadinessView.as_view(), name='ple-readiness'),
]
