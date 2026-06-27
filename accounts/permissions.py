from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "super_admin")


class IsAdminOrSuperAdmin(BasePermission):
    """Admin panel access. Super admin always passes."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in ("admin", "super_admin")
        )


class IsAgent(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "agent")


class IsAdminOrAgent(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in ("admin", "super_admin", "agent")
        )


class IsOwnerOrAdmin(BasePermission):
    """Object-level: owner of the object, or staff role, can write. Anyone can read."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.user.role in ("admin", "super_admin"):
            return True
        owner = getattr(obj, "user", None) or getattr(obj, "owner", None)
        return owner == request.user


class ReadOnlyOrAdminWrite(BasePermission):
    """Public can read (GET/HEAD/OPTIONS). Only admin/super_admin/agent can write."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in ("admin", "super_admin", "agent")
        )
