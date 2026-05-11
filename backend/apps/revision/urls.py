from django.urls import path
from .views import RevisionView

urlpatterns = [
    path('', RevisionView.as_view(), name='revision-list'),
]
