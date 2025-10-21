from rest_framework import permissions


class IsAdminOrSuperAdmin(permissions.BasePermission):
    """
    Custom permission to only allow admins to access their own vouchers,
    and superadmins to access all vouchers.
    """

    def has_permission(self, request, view):
        # Must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superadmin has access to everything
        if request.user.is_superuser:
            return True
        
        # Regular admin can access their own vouchers
        return request.user.is_staff

    def has_object_permission(self, request, view, obj):
        # Superadmin can access any voucher
        if request.user.is_superuser:
            return True
        
        # Admin can only access vouchers they created
        if hasattr(obj, 'creator'):
            return obj.creator == request.user
        
        return False


class IsSuperAdmin(permissions.BasePermission):
    """
    Permission to only allow superadmins.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_superuser
