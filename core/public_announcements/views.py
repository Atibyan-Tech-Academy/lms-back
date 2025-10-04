# public_announcements/views.py
from rest_framework import viewsets, permissions
from .models import PublicAnnouncement
from .serializers import PublicAnnouncementSerializer

class PublicAnnouncementViewSet(viewsets.ModelViewSet):
    queryset = PublicAnnouncement.objects.all()
    serializer_class = PublicAnnouncementSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]