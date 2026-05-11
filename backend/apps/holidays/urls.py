from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HolidayPackageViewSet

router = DefaultRouter()
router.register('', HolidayPackageViewSet, basename='holidays')

urlpatterns = [path('', include(router.urls))]
