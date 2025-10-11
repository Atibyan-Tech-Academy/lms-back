from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import UserProfile
from .serializers import UserProfileSerializer

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get", "put"], url_path="profile")
    def profile(self, request):
        profile = getattr(request.user, "profile", None)
        if not profile:
            return Response({"detail": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

        if request.method == "GET":
            serializer = self.get_serializer(profile)
            return Response(serializer.data)

        elif request.method == "PUT":
            # Restrict role and department updates to admins
            data = request.data.copy()
            if not request.user.is_superuser:
                if "role" in data:
                    return Response({"detail": "Role can only be updated by admin"}, status=status.HTTP_403_FORBIDDEN)
                if "department" in data:
                    return Response({"detail": "Department can only be updated by admin"}, status=status.HTTP_403_FORBIDDEN)
            serializer = self.get_serializer(profile, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            # Update user first_name / last_name
            first_name = data.get("first_name")
            last_name = data.get("last_name")
            password = data.get("password")
            user = request.user
            if first_name is not None:
                user.first_name = first_name
            if last_name is not None:
                user.last_name = last_name
            if password:
                user.set_password(password)
            user.save()

            return Response(self.get_serializer(profile).data)