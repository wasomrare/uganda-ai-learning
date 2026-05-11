from django.urls import path
from .views import (
    StudentAnalyticsView, MyAnalyticsView,
    ClassAnalyticsView, AdminDashboardAnalyticsView,
)

urlpatterns = [
    path('me/', MyAnalyticsView.as_view(), name='analytics-me'),
    path('student/<uuid:student_id>/', StudentAnalyticsView.as_view(), name='analytics-student'),
    path('class/<uuid:class_id>/', ClassAnalyticsView.as_view(), name='analytics-class'),
    path('admin/', AdminDashboardAnalyticsView.as_view(), name='analytics-admin'),
]
