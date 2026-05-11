"""Recommendation views."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers

from core.permissions import IsStudent, IsSuperAdminOrTeacher
from core.utils import success_response
from .models import LearningRecommendation


class RecommendationSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    topic_name = serializers.CharField(source='topic.name', read_only=True)

    class Meta:
        model = LearningRecommendation
        fields = ['id', 'recommendation_type', 'subject_name', 'topic_name',
                  'message', 'priority', 'estimated_time_minutes', 'is_completed', 'created_at']


class MyRecommendationsView(APIView):
    permission_classes = [IsStudent]

    def get(self, request):
        try:
            student = request.user.student_profile
        except Exception:
            return Response({'error': 'Profile not found.'}, status=404)

        recommendations = LearningRecommendation.objects.filter(
            student=student, is_completed=False
        ).select_related('subject', 'topic').order_by('-priority', '-created_at')[:10]

        return Response(success_response(RecommendationSerializer(recommendations, many=True).data))

    def patch(self, request, rec_id):
        try:
            student = request.user.student_profile
            rec = LearningRecommendation.objects.get(id=rec_id, student=student)
            rec.is_completed = True
            rec.save()
            return Response(success_response({}, 'Marked as completed.'))
        except LearningRecommendation.DoesNotExist:
            return Response({'error': 'Not found.'}, status=404)
