from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Allow administrators to access any user
        if request.user.role == 'administrator':
            return True
        # Allow users to access their own profile
        return obj.id == request.user.id 