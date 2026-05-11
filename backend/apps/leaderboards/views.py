"""Leaderboard views."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers
from django.utils import timezone

from core.permissions import IsSuperAdminOrTeacher, IsStudent
from core.utils import success_response
from .models import Leaderboard, LeaderboardEntry


class LeaderboardEntrySerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_class = serializers.CharField(source='student.class_name', read_only=True)
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = LeaderboardEntry
        fields = ['rank', 'student_name', 'student_class', 'avatar', 'score', 'xp', 'streak', 'assessments_completed', 'accuracy']

    def get_avatar(self, obj):
        if obj.student.photo:
            return obj.student.photo.url
        return None


class WeeklyLeaderboardView(APIView):
    permission_classes = [IsStudent]

    def get(self, request):
        today = timezone.now().date()
        import datetime
        week_start = today - datetime.timedelta(days=today.weekday())

        lb = Leaderboard.objects.filter(
            leaderboard_type='weekly',
            period_start=week_start,
        ).first()

        if not lb:
            return Response(success_response({'entries': [], 'my_rank': None}))

        entries = lb.entries.select_related('student__user').order_by('rank')[:20]

        my_rank = None
        try:
            student = request.user.student_profile
            my_entry = lb.entries.filter(student=student).first()
            if my_entry:
                my_rank = my_entry.rank
        except Exception:
            pass

        return Response(success_response({
            'period_start': str(lb.period_start),
            'period_end': str(lb.period_end),
            'entries': LeaderboardEntrySerializer(entries, many=True).data,
            'my_rank': my_rank,
        }))


class AdminLeaderboardView(APIView):
    permission_classes = [IsSuperAdminOrTeacher]

    def get(self, request):
        leaderboard_type = request.query_params.get('type', 'weekly')
        lb = Leaderboard.objects.filter(leaderboard_type=leaderboard_type).order_by('-period_start').first()
        if not lb:
            return Response(success_response({'entries': []}))
        entries = lb.entries.select_related('student__user').order_by('rank')[:50]
        return Response(success_response({
            'type': leaderboard_type,
            'entries': LeaderboardEntrySerializer(entries, many=True).data,
        }))
