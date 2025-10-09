# accounts/serializers.py
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from django.contrib.auth import authenticate
from django.db import models
from .models import User, PasswordResetCode, Roles
from editprofile.models import UserProfile
import logging

logger = logging.getLogger(__name__)

class UserSerializer(serializers.ModelSerializer):
    profile_image = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "first_name", "last_name",
            "student_id", "lecturer_id", "profile_image", "full_name",
            "role", "display_name", "theme_preference"
        ]

    def get_profile_image(self, obj):
        try:
            profile = obj.profile
            return profile.picture.url if profile.picture else None
        except UserProfile.DoesNotExist:
            return None

    def get_full_name(self, obj):
        try:
            return obj.profile.full_name
        except UserProfile.DoesNotExist:
            return f"{obj.first_name} {obj.last_name}".strip() or obj.display_name or obj.username

    def get_role(self, obj):
        try:
            return obj.profile.role
        except UserProfile.DoesNotExist:
            return obj.role

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    role = serializers.ChoiceField(choices=Roles.choices, required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "first_name", "last_name", "role"]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            role=validated_data["role"],
        )
        UserProfile.objects.get_or_create(
            user=user,
            defaults={"role": user.role, "full_name": f"{user.first_name} {user.last_name}"}
        )
        return user

class CustomTokenObtainSerializer(serializers.Serializer):
    identifier = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        identifier = attrs.get("identifier").strip() if attrs.get("identifier") else ""
        password = attrs.get("password").strip() if attrs.get("password") else ""

        logger.info(f"Login attempt with identifier: {identifier}")

        user = User.objects.filter(
            models.Q(email=identifier) |
            models.Q(username=identifier) |
            models.Q(student_id=identifier) |
            models.Q(lecturer_id=identifier)
        ).first()

        if not user:
            logger.warning(f"No user found for identifier: {identifier}")
            raise serializers.ValidationError({"identifier": "No user found with this identifier."})

        if user.email == identifier:
            authenticated_user = authenticate(username=user.email, password=password)
            if not authenticated_user:
                logger.warning(f"Invalid password for user email: {user.email}")
                raise serializers.ValidationError({"non_field_errors": ["Invalid credentials."]})
        else:
            if not user.check_password(password):
                logger.warning(f"Invalid password for user: {user.email}")
                raise serializers.ValidationError({"non_field_errors": ["Invalid credentials."]})

        if not user.is_active:
            logger.warning(f"User account disabled: {user.email}")
            raise serializers.ValidationError({"non_field_errors": ["User account is disabled."]})

        if not hasattr(user, "profile"):
            profile = UserProfile.objects.create(
                user=user,
                role=user.role,
                full_name=f"{user.first_name} {user.last_name}".strip() or user.username
            )
            logger.info(f"Created profile for login user {user.email}")

        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": UserSerializer(user).data,
            "role": user.profile.role if hasattr(user, "profile") else user.role
        }

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user found with this email.")
        return value

class PasswordResetVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        try:
            PasswordResetCode.objects.get(
                user__email=attrs["email"],
                code=attrs["code"],
                expires_at__gt=timezone.now(),
            )
        except PasswordResetCode.DoesNotExist:
            raise serializers.ValidationError("Invalid or expired verification code.")
        return attrs

class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        try:
            PasswordResetCode.objects.get(
                user__email=attrs["email"],
                code=attrs["code"],
                expires_at__gt=timezone.now(),
            )
        except PasswordResetCode.DoesNotExist:
            raise serializers.ValidationError("Invalid or expired verification code.")
        return attrs

    def save(self):
        email = self.validated_data["email"]
        new_password = self.validated_data["new_password"]
        user = User.objects.get(email=email)
        user.set_password(new_password)
        user.save()
        PasswordResetCode.objects.filter(user=user).delete()