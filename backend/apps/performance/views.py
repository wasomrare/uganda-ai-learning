from rest_framework.views import APIView
from rest_framework.response import Response
from core.permissions import IsStudent, IsSuperAdminOrTeacher
from core.utils import success_response
from .models import PLEReadinessScore


class PLEReadinessView(APIView):
    permission_classes = [IsSuperAdminOrTeacher]

    def get(self, request, student_id):
        try:
            score = PLEReadinessScore.objects.get(student_id=student_id)
            return Response(success_response({
                'overall': score.overall_score,
                'english': score.english_score,
                'mathematics': score.mathematics_score,
                'science': score.science_score,
                'sst': score.sst_score,
                'predicted_aggregate': score.predicted_aggregate,
                'confidence': score.confidence_level,
            }))
        except PLEReadinessScore.DoesNotExist:
            return Response(success_response(None, 'No PLE data yet.'))
