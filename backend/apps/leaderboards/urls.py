from django.urls import path
from .views import WeeklyLeaderboardView, AdminLeaderboardView

urlpatterns = [
    path('weekly/', WeeklyLeaderboardView.as_view(), name='leaderboard-weekly'),
    path('admin/', AdminLeaderboardView.as_view(), name='leaderboard-admin'),
]
