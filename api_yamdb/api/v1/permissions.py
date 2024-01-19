from rest_framework import permissions


class IsSuperUserOrIsAdminOnly(permissions.BasePermission):
    """
    Предоставляет доуступ только суперпользователю Джанго, админу Джанго или
    аутентифицированному пользователю с ролью админа.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_admin)


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Предоставляет доуступ только суперпользователю Джанго и админу Джанго.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_admin


class IsAdminModeratorAuthorOrReadOnly(permissions.BasePermission):
    """
    Предоставляет доступ только суперпользователю Джанго, админу Джанго,
    модератору и автору.
    """
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_moderator
            or request.user.is_admin
            or request.user == obj.author
        )
