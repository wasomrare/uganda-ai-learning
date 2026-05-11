"""Revision views."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers

from core.permissions import IsStudent
from core.utils import success_response
from .models import RevisionSession


class RevisionSessionSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    topic_name = serializers.CharField(source='topic.name', read_only=True)

    class Meta:
        model = RevisionSession
        fields = ['id', 'subject_name', 'topic_name', 'score', 'questions_attempted',
                  'questions_correct', 'duration_minutes', 'created_at']


class RevisionView(APIView):
    permission_classes = [IsStudent]

    def get(self, request):
        try:
            student = request.user.student_profile
        except Exception:
            return Response({'error': 'Profile not found.'}, status=404)
        sessions = RevisionSession.objects.filter(student=student).select_related('subject', 'topic').order_by('-created_at')[:20]
        return Response(success_response(RevisionSessionSerializer(sessions, many=True).data))

    def post(self, request):
        try:
            student = request.user.student_profile
        except Exception:
            return Response({'error': 'Profile not found.'}, status=404)

        from apps.subjects.models import Subject
        subject_id = request.data.get('subject_id')
        subject = Subject.objects.filter(id=subject_id).first() if subject_id else None

        session = RevisionSession.objects.create(
            student=student,
            subject=subject,
            score=request.data.get('score', 0),
            questions_attempted=request.data.get('questions_attempted', 0),
            questions_correct=request.data.get('questions_correct', 0),
            duration_minutes=request.data.get('duration_minutes', 0),
        )

        from apps.gamification.models import award_xp
        xp_earned = session.questions_correct * 5
        if xp_earned > 0:
            award_xp(student, xp_earned, f'revision_{subject.name if subject else "general"}')

        return Response(success_response({'session_id': str(session.id), 'xp_earned': xp_earned}, 'Session saved.'), status=201)
