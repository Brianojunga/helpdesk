from rest_framework.permissions import BasePermission

class CanAssignAgent(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return (
            user.is_authenticated and
            user.role in ['owner', 'admin']
        )