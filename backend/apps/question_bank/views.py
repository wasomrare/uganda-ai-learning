"""Question bank views."""
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from core.permissions import IsSuperAdmin, IsSuperAdminOrTeacher, IsStudent
from core.utils import success_response
from .models import Question
from .serializers import (
    QuestionListSerializer, QuestionDetailSerializer,
    QuestionStudentSerializer, CreateQuestionSerializer,
)


class QuestionViewSet(ModelViewSet):
    queryset = Question.objects.select_related(
        'subject', 'topic', 'subtopic'
    ).prefetch_related('options', 'answer', 'matching_pairs', 'segments').filter(is_active=True)

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        'question_type', 'subject', 'topic', 'class_level',
        'term', 'difficulty', 'source', 'is_approved',
    ]
    search_fields = ['question_text', 'tags']
    ordering_fields = ['-created_at', 'difficulty', 'use_count', 'correct_rate']
    ordering = ['-created_at']

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsSuperAdminOrTeacher()]
        return [IsSuperAdmin()]

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateQuestionSerializer
        if self.action == 'list':
            return QuestionListSerializer
        return QuestionDetailSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, source='teacher_created')

    @action(detail=True, methods=['post'], permission_classes=[IsSuperAdminOrTeacher])
    def approve(self, request, pk=None):
        question = self.get_object()
        question.is_approved = True
        question.save()
        return Response(success_response({}, 'Question approved.'))

    @action(detail=True, methods=['post'], permission_classes=[IsSuperAdminOrTeacher])
    def reject(self, request, pk=None):
        question = self.get_object()
        question.is_approved = False
        question.is_active = False
        question.save()
        return Response(success_response({}, 'Question rejected.'))

    @action(detail=False, methods=['get'], permission_classes=[IsSuperAdminOrTeacher])
    def pending_approval(self, request):
        qs = self.get_queryset().filter(is_approved=False, source='ai_generated')
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(QuestionListSerializer(page, many=True).data)
        return Response(success_response(QuestionListSerializer(qs, many=True).data))

    @action(detail=False, methods=['get'], permission_classes=[IsSuperAdminOrTeacher])
    def stats(self, request):
        from django.db.models import Count, Avg
        stats = {
            'total': Question.objects.count(),
            'approved': Question.objects.filter(is_approved=True).count(),
            'pending': Question.objects.filter(is_approved=False, is_active=True).count(),
            'by_type': list(Question.objects.values('question_type').annotate(count=Count('id'))),
            'by_difficulty': list(Question.objects.values('difficulty').annotate(count=Count('id'))),
            'by_source': list(Question.objects.values('source').annotate(count=Count('id'))),
            'avg_correct_rate': Question.objects.aggregate(avg=Avg('correct_rate'))['avg'] or 0,
        }
        return Response(success_response(stats))

    @action(detail=False, methods=['post'], permission_classes=[IsSuperAdminOrTeacher])
    def bulk_approve(self, request):
        ids = request.data.get('question_ids', [])
        updated = Question.objects.filter(id__in=ids).update(is_approved=True)
        return Response(success_response({'approved_count': updated}, f'{updated} questions approved.'))
