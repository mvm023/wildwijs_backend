from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminForUnsafeMethods(BasePermission):
    """
    - Allows *anyone* to perform safe methods (GET, HEAD, OPTIONS)
    - Only allows *admin users* to perform unsafe methods (POST, PUT, DELETE, etc.)
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and request.user.is_superuser

class isAdminForAllMethods(BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_superuser