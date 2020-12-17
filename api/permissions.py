from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    message = "You should be an admin to modify this object"

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_staff


class IsOwnerOrReadOnly(permissions.BasePermission):
    message = "You should be an owner to modify this object"

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.creator == request.user
