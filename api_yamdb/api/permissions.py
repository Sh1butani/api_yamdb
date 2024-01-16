from rest_framework import permissions


class AnonimReadOnly(permissions.BasePermission):
    """Разрешает анонимному пользователю только безопасные запросы."""

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsSuperUserOrIsAdminOnly(permissions.BasePermission):
    """
    Предоставляет доуступ только суперпользователю Джанго, админу Джанго или
    аутентифицированному пользователю с ролью admin.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (request.user.is_superuser
                 or request.user.is_staff
                 or request.user.is_admin)
        )


class IsSuperUserIsAdminIsModeratorIsAuthor(permissions.BasePermission):
    """
    Предоставляет доуступ только суперпользователю Джанго, админу Джанго,
    аутентифицированным пользователям с ролью admin или moderator,
    а также автору объекта.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated
            and (request.user.is_superuser
                 or request.user.is_staff
                 or request.user.is_admin
                 or request.user.is_moderator
                 or request.user == obj.author)
        )
