from django.urls import path
from .views import MyRecommendationsView

urlpatterns = [
    path('mine/', MyRecommendationsView.as_view(), name='recommendations-mine'),
    path('mine/<uuid:rec_id>/complete/', MyRecommendationsView.as_view(), name='recommendations-complete'),
]
