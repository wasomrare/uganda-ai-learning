from rest_framework.views import APIView
from rest_framework.response import Response
from core.permissions import IsSuperAdminOrTeacher
from core.utils import success_response
from .models import Report


class ReportView(APIView):
    permission_classes = [IsSuperAdminOrTeacher]

    def get(self, request):
        reports = Report.objects.filter(generated_by=request.user).order_by('-created_at')[:20]
        return Response(success_response([{
            'id': str(r.id),
            'title': r.title,
            'type': r.report_type,
            'status': r.status,
            'file_url': request.build_absolute_uri(r.file.url) if r.file else None,
            'created_at': r.created_at.isoformat(),
        } for r in reports]))

    def post(self, request):
        report = Report.objects.create(
            title=request.data.get('title', 'Report'),
            report_type=request.data.get('report_type', 'analytics_report'),
            generated_by=request.user,
            parameters=request.data.get('parameters', {}),
        )
        return Response(success_response({'id': str(report.id)}, 'Report queued.'), status=201)
