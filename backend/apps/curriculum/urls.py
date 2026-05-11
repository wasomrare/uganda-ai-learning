from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TopicViewSet, LearningResourceViewSet

router = DefaultRouter()
router.register('topics', TopicViewSet, basename='topics')
router.register('resources', LearningResourceViewSet, basename='resources')

urlpatterns = [path('', include(router.urls))]
