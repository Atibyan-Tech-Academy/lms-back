from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import UserSerializer, RegisterSerializer, CustomTokenObtainSerializer
from django.middleware.csrf import get_token
import logging

logger = logging.getLogger(__name__)

# Register
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

# Profile (get/update logged-in user)
class ProfileView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        data = self.get_serializer(user).data
        if user.profile_image:
            data["profile_image"] = request.build_absolute_uri(user.profile_image.url)
        return Response(data)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        user = self.get_object()
        if user.profile_image:
            response.data["profile_image"] = request.build_absolute_uri(user.profile_image.url)
        return response

# Custom Login (identifier = email / student_id / lecturer_id / username)
class CustomLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        logger.info(f"Received login data: {request.data}")
        serializer = CustomTokenObtainSerializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=400)
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "role": user.role,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "student_id": user.student_id,
                "lecturer_id": user.lecturer_id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "profile_image": (
                    request.build_absolute_uri(user.profile_image.url) if user.profile_image else None
                ),
            }
        })

# CSRF Token Endpoint
class GetCSRFToken(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        return Response({'csrfToken': get_token(request)})