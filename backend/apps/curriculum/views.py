from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from core.permissions import IsSuperAdmin, IsSuperAdminOrTeacher
from core.utils import success_response
from .models import Topic, SubTopic, LearningResource
from .serializers import TopicListSerializer, TopicDetailSerializer, SubTopicSerializer, LearningResourceSerializer


class TopicViewSet(ModelViewSet):
    queryset = Topic.objects.select_related('subject').prefetch_related('subtopics', 'resources').filter(is_active=True)
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['subject', 'class_level', 'term', 'week', 'difficulty']
    search_fields = ['name', 'description']
    ordering_fields = ['class_level', 'term', 'week', 'order']
    ordering = ['class_level', 'term', 'week', 'order']

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsSuperAdminOrTeacher()]
        return [IsSuperAdmin()]

    def get_serializer_class(self):
        if self.action == 'list':
            return TopicListSerializer
        return TopicDetailSerializer

    @action(detail=False, methods=['get'])
    def by_class_subject(self, request):
        class_level = request.query_params.get('class_level')
        subject_id = request.query_params.get('subject_id')
        term = request.query_params.get('term')

        qs = self.get_queryset()
        if class_level:
            qs = qs.filter(class_level=class_level)
        if subject_id:
            qs = qs.filter(subject_id=subject_id)
        if term:
            qs = qs.filter(term=term)

        serializer = TopicListSerializer(qs, many=True)
        return Response(success_response(serializer.data))


class LearningResourceViewSet(ModelViewSet):
    queryset = LearningResource.objects.select_related('topic', 'uploaded_by').filter(is_active=True)
    serializer_class = LearningResourceSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['topic', 'resource_type', 'is_approved']
    search_fields = ['title']

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsSuperAdminOrTeacher()]
        return [IsSuperAdminOrTeacher()]

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)
