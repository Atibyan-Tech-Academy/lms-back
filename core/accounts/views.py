from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, PasswordResetCode, Roles
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
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                "role": user.role,
                "full_name": f"{user.first_name} {user.last_name}".strip() or user.display_name or user.username,
            }
        )
        if created:
            logger.info(f"Created UserProfile for {user.email}")
        data = self.get_serializer(user).data
        if profile.picture:
            data["profile_image"] = request.build_absolute_uri(profile.picture.url)
        else:
            data["profile_image"] = None
        data["full_name"] = profile.full_name
        data["role"] = profile.role
        return Response(data)

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                "role": user.role,
                "full_name": f"{user.first_name} {user.last_name}".strip() or user.display_name or user.username,
            }
        )
        if created:
            logger.info(f"Created UserProfile for {user.email} during update")
        partial = True
        user_serializer = self.get_serializer(user, data=request.data, partial=partial)
        if user_serializer.is_valid():
            user_serializer.save()
            if "full_name" in request.data:
                profile.full_name = request.data["full_name"]
            if "picture" in request.FILES:
                profile.picture = request.FILES["picture"]
            if "role" in request.data:
                new_role = request.data["role"]
                if new_role in [choice[0] for choice in Roles.choices]:
                    user.role = new_role
                    profile.role = new_role
                    user.save()
            profile.save()
            updated_data = self.get_serializer(user).data
            if profile.picture:
                updated_data["profile_image"] = request.build_absolute_uri(profile.picture.url)
            else:
                updated_data["profile_image"] = None
            updated_data["full_name"] = profile.full_name
            updated_data["role"] = profile.role
            return Response(updated_data)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserListView(generics.ListAPIView):
    queryset = User.objects.all().select_related('profile')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

class CustomLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = CustomTokenObtainSerializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Login error: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        user_data = data["user"]
        role = data["role"]
        refresh = data["refresh"]
        access = data["access"]

        return Response({
            "refresh": refresh,
            "access": access,
            "role": role,
            "user": user_data
        })

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
                    UserProfile.objects.create(
                        user=user,
                        role=user.role,
                        full_name=user.display_name or f"{user.first_name} {user.last_name}"
                    )
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