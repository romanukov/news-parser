from rest_framework.permissions import BasePermission


class IsSubscribedPermission(BasePermission):
    message = "Your subscription expired."
    def has_permission(self, request, view):
        return request.user.check_subscribe()