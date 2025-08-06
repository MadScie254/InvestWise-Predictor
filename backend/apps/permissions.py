from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsOwnerOrAdmin(BasePermission):
    """
    Custom permission to only allow owners of an object or admins to edit/view it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the prediction or admins
        return obj.user == request.user or request.user.is_staff


class IsOwnerOrReadOnly(BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    Others can only read.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        return obj.user == request.user


class IsAdminOrReadOnly(BasePermission):
    """
    Custom permission to only allow admins to edit.
    Regular users can only read.
    """
    
    def has_permission(self, request, view):
        # Read permissions are allowed to any authenticated request
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        # Write permissions are only allowed to admin users
        return request.user.is_staff


class IsPredictionOwner(BasePermission):
    """
    Custom permission specifically for prediction objects.
    """
    
    def has_object_permission(self, request, view, obj):
        # Check if the user is the owner of the prediction
        return obj.user == request.user


class CanManagePredictions(BasePermission):
    """
    Permission for users who can manage predictions.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_staff or 
            request.user.has_perm('apps.change_prediction')
        )
