from rest_framework.views import APIView
from rest_framework.response import Response
from core.permissions import IsParent
from core.utils import success_response


class ChildrenView(APIView):
    permission_classes = [IsParent]

    def get(self, request):
        children = request.user.children.all().select_related('student__current_class')
        return Response(success_response([{
            'name': c.student.full_name,
            'class': c.student.class_name,
            'admission': c.student.admission_number,
            'relationship': c.relationship,
        } for c in children]))


class ChildPerformanceView(APIView):
    permission_classes = [IsParent]

    def get(self, request, student_id):
        from apps.students.models import Student
        try:
            guardian = request.user.children.get(student_id=student_id)
            student = guardian.student
        except Exception:
            return Response({'error': 'Child not found or access denied.'}, status=403)

        from apps.analytics.services import get_student_performance_summary
        return Response(success_response(get_student_performance_summary(student)))
