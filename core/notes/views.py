from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .models import Note
from .serializers import NoteSerializer

class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Note.objects.filter(student=self.request.user)

    def perform_create(self, serializer):
        if self.request.user.profile.role != "STUDENT":
            return Response({"detail": "Only students can create notes."}, status=403)
        serializer.save(student=self.request.user)

    def perform_update(self, serializer):
        if self.request.user.profile.role != "STUDENT":
            return Response({"detail": "Only students can update notes."}, status=403)
        serializer.save(student=self.request.user)