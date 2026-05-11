from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SubjectViewSet

router = DefaultRouter()
router.register('', SubjectViewSet, basename='subjects')

urlpatterns = [path('', include(router.urls))]
