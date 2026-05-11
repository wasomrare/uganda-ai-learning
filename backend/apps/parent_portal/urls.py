from django.urls import path
from .views import ChildrenView, ChildPerformanceView

urlpatterns = [
    path('children/', ChildrenView.as_view(), name='parent-children'),
    path('children/<uuid:student_id>/performance/', ChildPerformanceView.as_view(), name='parent-child-performance'),
]
