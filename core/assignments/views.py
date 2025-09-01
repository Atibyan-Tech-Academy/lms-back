from rest_framework import viewsets, permissions
from .models import Assignment, Submission
from .serializers import AssignmentSerializer, SubmissionSerializer
from .permissions import IsInstructor, IsStudent, IsOwnerOrInstructor
from accounts.models import Roles


class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [permissions.IsAuthenticated(), IsInstructor()]
        return [permissions.IsAuthenticated()]  # anyone logged in can view


class SubmissionViewSet(viewsets.ModelViewSet):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer

    def get_permissions(self):
        if self.action == "create":
            return [permissions.IsAuthenticated(), IsStudent()]
        elif self.action in ["update", "partial_update", "destroy"]:
            return [permissions.IsAuthenticated(), IsInstructor()]
        return [permissions.IsAuthenticated(), IsOwnerOrInstructor()]
    