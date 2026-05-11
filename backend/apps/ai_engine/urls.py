from django.urls import path
from .views import (
    GenerateQuestionsView, GenerateHolidayPackageView,
    AIChatView, AIStatusView, TriggerMarkingView,
)

urlpatterns = [
    path('generate/questions/', GenerateQuestionsView.as_view(), name='ai-generate-questions'),
    path('generate/holiday/', GenerateHolidayPackageView.as_view(), name='ai-generate-holiday'),
    path('chat/', AIChatView.as_view(), name='ai-chat'),
    path('status/', AIStatusView.as_view(), name='ai-status'),
    path('mark/', TriggerMarkingView.as_view(), name='ai-mark'),
]
