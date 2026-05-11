from django.urls import path
from .views import ChatHistoryView

urlpatterns = [
    path('<str:room>/history/', ChatHistoryView.as_view(), name='chat-history'),
]
