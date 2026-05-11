"""Custom permissions for Uganda Primary AI Learning System."""
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsSuperAdmin(BasePermission):
    """Only super admins can access."""
    message = 'Super admin access required.'

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'super_admin'
        )


class IsTeacher(BasePermission):
    """Only teachers can access."""
    message = 'Teacher access required.'

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'teacher'
        )


class IsStudent(BasePermission):
    """Only students can access."""
    message = 'Student access required.'

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'student'
        )


class IsParent(BasePermission):
    """Only parents can access."""
    message = 'Parent access required.'

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'parent'
        )


class IsSuperAdminOrTeacher(BasePermission):
    """Super admin or teacher access."""
    message = 'Admin or teacher access required.'

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ('super_admin', 'teacher')
        )


class IsSuperAdminOrReadOnly(BasePermission):
    """Super admin for write, anyone authenticated for read."""
    message = 'Super admin access required for modifications.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.role == 'super_admin'


class IsOwnerOrSuperAdmin(BasePermission):
    """Object-level: owner or super admin."""

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'super_admin':
            return True
        return hasattr(obj, 'user') and obj.user == request.user


class IsStudentOwner(BasePermission):
    """Student can only access their own data."""

    def has_object_permission(self, request, view, obj):
        if request.user.role in ('super_admin', 'teacher'):
            return True
        return hasattr(obj, 'student') and obj.student.user == request.user


class CanManageClass(BasePermission):
    """Teacher can only manage their own classes."""
    message = 'You are not assigned to this class.'

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'super_admin':
            return True
        if request.user.role == 'teacher':
            teacher = getattr(request.user, 'teacher_profile', None)
            if teacher:
                return obj.teachers.filter(id=teacher.id).exists()
        return False


class CanCreateAccounts(BasePermission):
    """Only super admin can create user accounts."""
    message = 'Only administrators can create accounts.'

    def has_permission(self, request, view):
        if request.method == 'POST':
            return (
                request.user and
                request.user.is_authenticated and
                request.user.role == 'super_admin'
            )
        return request.user and request.user.is_authenticated
