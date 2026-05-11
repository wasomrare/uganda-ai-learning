from django.urls import path
from .views import GamificationProfileView, AllBadgesView

urlpatterns = [
    path('profile/', GamificationProfileView.as_view(), name='gamification-profile'),
    path('badges/', AllBadgesView.as_view(), name='gamification-badges'),
]
