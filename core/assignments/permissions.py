from rest_framework import permissions
from accounts.models import Roles


class IsInstructor(permissions.BasePermission):
    """Allow only instructors to create/edit assignments."""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == Roles.LECTURER


class IsStudent(permissions.BasePermission):
    """Allow only students to submit assignments."""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == Roles.STUDENT


class IsOwnerOrInstructor(permissions.BasePermission):
    """Students can see their own submissions, instructors can see all."""
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated and request.user.role == Roles.LECTURER:
            return True  # Instructors can view/edit all submissions
        # Check if obj has a 'student' attribute (for Submission objects)
        if hasattr(obj, 'student'):
            return obj.student == request.user  # Students only see their own submissions
        return False  # Deny access if obj is not a Submission or user is not owner