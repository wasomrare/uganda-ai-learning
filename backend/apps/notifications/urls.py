from django.urls import path
from .views import MyNotificationsView, AdminBroadcastView, AnnouncementsView

urlpatterns = [
    path('mine/', MyNotificationsView.as_view(), name='notifications-mine'),
    path('broadcast/', AdminBroadcastView.as_view(), name='notifications-broadcast'),
    path('announcements/', AnnouncementsView.as_view(), name='notifications-announcements'),
]
