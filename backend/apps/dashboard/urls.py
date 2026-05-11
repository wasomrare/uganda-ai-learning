from django.urls import path
from .views import AdminDashboardView, TeacherDashboardView, StudentDashboardView

urlpatterns = [
    path('admin/', AdminDashboardView.as_view(), name='dashboard-admin'),
    path('teacher/', TeacherDashboardView.as_view(), name='dashboard-teacher'),
    path('student/', StudentDashboardView.as_view(), name='dashboard-student'),
]
