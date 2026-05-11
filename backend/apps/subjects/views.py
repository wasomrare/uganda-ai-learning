from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from core.permissions import IsSuperAdmin, IsSuperAdminOrTeacher
from .models import Subject
from .serializers import SubjectSerializer


class SubjectViewSet(ModelViewSet):
    queryset = Subject.objects.filter(is_active=True)
    serializer_class = SubjectSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'is_examinable', 'is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['order', 'name']
    ordering = ['order']

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsSuperAdminOrTeacher()]
        return [IsSuperAdmin()]
