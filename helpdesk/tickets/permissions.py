from rest_framework.permissions import BasePermission

class CanAccessTicketResolution(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if  user.is_authenticated and user.role in ['owner', 'admin','agent']:
            if obj.company == user.company and obj.status == 'closed':
                return True
        return False