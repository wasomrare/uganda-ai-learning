"""User management views — admin only."""
from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from core.permissions import IsSuperAdmin, IsSuperAdminOrTeacher, CanCreateAccounts
from core.utils import generate_secure_password, success_response
from .models import User
from .serializers import (
    UserListSerializer, UserDetailSerializer,
    CreateUserSerializer, ChangePasswordSerializer,
    AdminResetPasswordSerializer,
)


class UserViewSet(ModelViewSet):
    """CRUD for users — super admin only."""
    queryset = User.objects.select_related('profile').all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['role', 'is_active', 'is_verified']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering_fields = ['created_at', 'last_login', 'first_name']
    ordering = ['-created_at']

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsSuperAdminOrTeacher()]
        return [IsSuperAdmin()]

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateUserSerializer
        if self.action in ('list',):
            return UserListSerializer
        return UserDetailSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsSuperAdmin])
    def reset_password(self, request, pk=None):
        user = self.get_object()
        serializer = AdminResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if serializer.validated_data.get('auto_generate', True):
            new_password = generate_secure_password()
        else:
            new_password = serializer.validated_data.get('new_password')
            if not new_password:
                return Response({'error': 'new_password is required.'}, status=400)

        user.set_password(new_password)
        user.force_password_change = True
        user.save()

        return Response(success_response(
            {'temporary_password': new_password},
            'Password reset successfully.',
        ))

    @action(detail=True, methods=['post'], permission_classes=[IsSuperAdmin])
    def toggle_active(self, request, pk=None):
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()
        status_text = 'activated' if user.is_active else 'deactivated'
        return Response(success_response({}, f'User {status_text} successfully.'))

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = UserDetailSerializer(request.user)
        return Response(success_response(serializer.data))

    @action(detail=False, methods=['post'], permission_classes=[])
    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'error': 'Current password is incorrect.'}, status=400)

        user.set_password(serializer.validated_data['new_password'])
        user.force_password_change = False
        user.save()
        return Response(success_response({}, 'Password changed successfully.'))

    @action(detail=False, methods=['get'], permission_classes=[IsSuperAdmin])
    def stats(self, request):
        from django.db.models import Count
        stats = User.objects.values('role').annotate(count=Count('id'))
        total = User.objects.count()
        active = User.objects.filter(is_active=True).count()
        return Response(success_response({
            'total': total,
            'active': active,
            'by_role': {item['role']: item['count'] for item in stats},
        }))
