# notes/views.py
from rest_framework import viewsets, permissions
from .models import Note
from .serializers import NoteSerializer

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class NoteViewSet(viewsets.ModelViewSet):
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        # Only notes of the current user
        return Note.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
<<<<<<< Updated upstream
        serializer.save(user=self.request.user)
=======
        serializer.save(user=self.request.user)
>>>>>>> Stashed changes
