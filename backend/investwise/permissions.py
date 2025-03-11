from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.conf import settings

# ===========================
# 1. Base Custom Permission Class
# ===========================

class IsAuthenticatedOrReadOnly(BasePermission):
    """
    Allows access to authenticated users for unsafe methods (POST, PUT, DELETE).
    Allows read-only access (GET, HEAD, OPTIONS) for unauthenticated users.
    """

    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS or
            request.user and request.user.is_authenticated
        )


# ===========================
# 2. Role-Based Permissions
# ===========================

class IsAdminUser(BasePermission):
    """
    Allows access only to admin users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)


class IsInvestor(BasePermission):
    """
    Allows access only to users with the 'investor' role.
    Assumes the User model has a 'role' field.
    """

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            getattr(request.user, 'role', None) == 'investor'
        )


class IsEntrepreneur(BasePermission):
    """
    Allows access only to users with the 'entrepreneur' role.
    Assumes the User model has a 'role' field.
    """

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            getattr(request.user, 'role', None) == 'entrepreneur'
        )


# ===========================
# 3. Object-Level Permissions
# ===========================

class IsOwnerOrAdmin(BasePermission):
    """
    Allows access to the object owner or admin users.
    Assumes the object has an 'owner' field referencing the User model.
    """

    def has_object_permission(self, request, view, obj):
        # Admin users have full access
        if request.user and request.user.is_staff:
            return True

        # Check if the user is the owner of the object
        return bool(
            request.user and
            request.user.is_authenticated and
            obj.owner == request.user
        )


# ===========================
# 4. Custom Permissions for Sensitive Data
# ===========================

class CanAccessSensitiveData(BasePermission):
    """
    Allows access to sensitive data only for users with special permissions.
    Assumes the User model has a 'can_access_sensitive_data' boolean field.
    """

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            getattr(request.user, 'can_access_sensitive_data', False)
        )


# ===========================
# 5. IP Whitelisting Permission
# ===========================

class IsWhitelistedIP(BasePermission):
    """
    Allows access only from whitelisted IP addresses.
    Useful for securing sensitive endpoints.
    """

    def has_permission(self, request, view):
        whitelisted_ips = getattr(settings, 'WHITELISTED_IPS', [])
        client_ip = self.get_client_ip(request)
        return client_ip in whitelisted_ips

    @staticmethod
    def get_client_ip(request):
        """
        Extract the client's IP address from the request.
        """
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        return x_forwarded_for.split(",")[0] if x_forwarded_for else request.META.get("REMOTE_ADDR")


# ===========================
# 6. Combined Permissions
# ===========================

class IsAdminOrInvestor(BasePermission):
    """
    Allows access to admin users or users with the 'investor' role.
    """

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.is_staff or getattr(request.user, 'role', None) == 'investor')
        )
