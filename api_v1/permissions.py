from rest_framework import permissions

class SketchPermission(permissions.BasePermission):
    """
    Разрешение для эскизов тату-салона:
    - создавать эскизы могут все (даже анонимы).
    - изменять и удалять — только авторизованные мастера/пользователи.
    """

    def has_permission(self, request, view):
        if view.action == 'create' or request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated