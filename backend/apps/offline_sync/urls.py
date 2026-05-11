from django.urls import path
from .views import SyncUploadView, SyncStatusView, OfflineDataDownloadView

urlpatterns = [
    path('upload/', SyncUploadView.as_view(), name='sync-upload'),
    path('status/', SyncStatusView.as_view(), name='sync-status'),
    path('download/', OfflineDataDownloadView.as_view(), name='sync-download'),
]
