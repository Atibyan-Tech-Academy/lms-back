from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, PasswordResetCode
from .serializers import UserSerializer, RegisterSerializer, CustomTokenObtainSerializer, PasswordResetRequestSerializer, PasswordResetVerifySerializer, PasswordResetConfirmSerializer
from django.middleware.csrf import get_token
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
import logging
import random
import string
from editprofile.models import UserProfile

logger = logging.getLogger(__name__)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class ProfileView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        try:
            profile = user.profile
            data = self.get_serializer(user).data
            data["profile_image"] = request.build_absolute_uri(profile.picture.url) if profile.picture else user.get_initial_avatar()
            data["full_name"] = profile.full_name
            data["role"] = profile.role
            return Response(data)
        except UserProfile.DoesNotExist:
            logger.error(f"No UserProfile for {user.email}")
            return Response({"detail": "User profile not found."}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        try:
            profile = user.profile
            response = super().update(request, *args, **kwargs)
            if "full_name" in request.data:
                profile.full_name = request.data["full_name"]
            if "role" in request.data and request.data["role"] in [choice[0] for choice in UserProfile.Role.choices]:
                profile.role = request.data["role"]
            if "picture" in request.data:
                profile.picture = request.data["picture"]
            profile.save()
            response.data["profile_image"] = request.build_absolute_uri(profile.picture.url) if profile.picture else user.get_initial_avatar()
            response.data["full_name"] = profile.full_name
            response.data["role"] = profile.role
            return response
        except UserProfile.DoesNotExist:
            logger.error(f"No UserProfile for {user.email}")
            return Response({"detail": "User profile not found."}, status=status.HTTP_404_NOT_FOUND)

class CustomLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = CustomTokenObtainSerializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Login error: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.validated_data["user"]
        try:
            profile = user.profile
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "role": profile.role,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "student_id": user.student_id,
                    "lecturer_id": user.lecturer_id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "profile_image": request.build_absolute_uri(profile.picture.url) if profile.picture else user.get_initial_avatar(),
                    "full_name": profile.full_name,
                    "role": profile.role,
                }
            })
        except UserProfile.DoesNotExist:
            logger.error(f"No UserProfile for {user.email}")
            return Response({"detail": "User profile not found."}, status=status.HTTP_404_NOT_FOUND)

class GetCSRFToken(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({"csrfToken": get_token(request)})

class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            try:
                user = User.objects.get(email=email)
                if not hasattr(user, "profile"):
                    UserProfile.objects.create(user=user, role=user.role, full_name=user.display_name or f"{user.first_name} {user.last_name}")
                code = ''.join(random.choices(string.digits, k=6))
                PasswordResetCode.objects.create(user=user, code=code)
                subject = "Password Reset Verification Code"
                context = {"code": code, "user": user, "admin_email": settings.ADMIN_EMAIL}
                html_message = render_to_string("email/password_reset.html", context)
                plain_message = f"Your verification code is: {code}\nValid for 15 minutes."
                send_mail(
                    subject,
                    plain_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                    html_message=html_message,
                )
                logger.info(f"Reset code sent to {email}")
                return Response({"detail": "Verification code sent."}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                logger.error(f"No user with email: {email}")
                return Response({"detail": "No user found."}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.error(f"Error sending code to {email}: {str(e)}")
                return Response({"detail": f"Failed to send code: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetVerifyView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetVerifySerializer(data=request.data)
        if serializer.is_valid():
            return Response({"detail": "Verification code valid."}, status=status.HTTP_200_OK)
        logger.error(f"Verification failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                logger.info(f"Password reset for {serializer.validated_data['email']}")
                return Response({"detail": "Password reset successful."}, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Reset failed: {str(e)}")
                return Response({"detail": f"Failed to reset password: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        logger.error(f"Reset validation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)