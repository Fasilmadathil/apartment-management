from rest_framework.permissions import BasePermission


class IsLandlord(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role and
            request.user.role.name in ['admin']
        )


class IsTenant(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role and
            request.user.role.name == 'tenant'
        )
