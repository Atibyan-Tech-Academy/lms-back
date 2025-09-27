from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import UserProfile
from .serializers import UserProfileSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get", "put"], url_path="profile")
    def profile(self, request):
        profile = request.user.profile
        if request.method == "GET":
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        elif request.method == "PUT":
            serializer = self.get_serializer(profile, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            # Update password if provided
            password = request.data.get("password")
            if password:
                user = request.user
                user.set_password(password)
                user.save()

            return Response(serializer.data)
