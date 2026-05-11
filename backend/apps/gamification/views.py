"""Gamification views."""
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.views import APIView
from rest_framework import serializers

from core.permissions import IsSuperAdminOrTeacher, IsStudent
from core.utils import success_response
from .models import Badge, StudentBadge, StudentXP, Streak


class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = ['id', 'name', 'description', 'category', 'icon', 'color', 'image',
                  'xp_reward', 'coin_reward', 'rarity', 'is_active']


class StudentBadgeSerializer(serializers.ModelSerializer):
    badge = BadgeSerializer(read_only=True)

    class Meta:
        model = StudentBadge
        fields = ['id', 'badge', 'earned_at', 'context']


class StudentXPSerializer(serializers.ModelSerializer):
    xp_for_next_level = serializers.IntegerField(read_only=True)
    xp_progress = serializers.FloatField(read_only=True)

    class Meta:
        model = StudentXP
        fields = ['total_xp', 'level', 'coins', 'weekly_xp', 'monthly_xp',
                  'xp_for_next_level', 'xp_progress', 'updated_at']


class GamificationProfileView(APIView):
    """Student's full gamification profile."""
    permission_classes = [IsStudent]

    def get(self, request):
        try:
            student = request.user.student_profile
        except Exception:
            return Response({'error': 'Student not found.'}, status=404)

        xp, _ = StudentXP.objects.get_or_create(student=student)
        streak, _ = Streak.objects.get_or_create(student=student)
        badges = StudentBadge.objects.filter(student=student).select_related('badge')
        recent_badges = badges.order_by('-earned_at')[:5]

        return Response(success_response({
            'xp': StudentXPSerializer(xp).data,
            'streak': {
                'current': streak.current_streak,
                'longest': streak.longest_streak,
                'total_active_days': streak.total_active_days,
                'last_activity': streak.last_activity_date,
            },
            'total_badges': badges.count(),
            'recent_badges': StudentBadgeSerializer(recent_badges, many=True).data,
        }))


class AllBadgesView(APIView):
    """List all available badges."""
    permission_classes = [IsStudent]

    def get(self, request):
        badges = Badge.objects.filter(is_active=True)
        try:
            student = request.user.student_profile
            earned_ids = set(StudentBadge.objects.filter(student=student).values_list('badge_id', flat=True))
        except Exception:
            earned_ids = set()

        result = []
        for badge in badges:
            data = BadgeSerializer(badge).data
            data['earned'] = badge.id in earned_ids
            result.append(data)

        return Response(success_response(result))
