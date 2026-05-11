from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from core.permissions import IsSuperAdminOrTeacher
from core.utils import success_response
from core.validators import validate_file_size, validate_file_extension
from .models import Upload


class UploadView(APIView):
    permission_classes = [IsSuperAdminOrTeacher]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided.'}, status=400)
        try:
            validate_file_size(file)
            validate_file_extension(file)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

        upload = Upload.objects.create(
            uploaded_by=request.user,
            file=file,
            original_name=file.name,
            file_type=file.content_type or '',
            file_size=file.size,
        )
        return Response(success_response({
            'id': str(upload.id),
            'url': request.build_absolute_uri(upload.file.url),
            'original_name': upload.original_name,
        }, 'File uploaded.'), status=201)

    def get(self, request):
        uploads = Upload.objects.filter(uploaded_by=request.user).order_by('-created_at')[:20]
        return Response(success_response([{
            'id': str(u.id),
            'original_name': u.original_name,
            'file_type': u.file_type,
            'file_size': u.file_size,
            'url': request.build_absolute_uri(u.file.url),
            'created_at': u.created_at.isoformat(),
        } for u in uploads]))
