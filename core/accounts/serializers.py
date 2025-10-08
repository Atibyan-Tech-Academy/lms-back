from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from django.contrib.auth import authenticate
from django.db import models
from .models import User, PasswordResetCode, Roles
from editprofile.models import UserProfile

class UserSerializer(serializers.ModelSerializer):
    profile_image = serializers.SerializerMethodField()
    full_name = serializers.CharField(source="profile.full_name", allow_null=True)
    role = serializers.CharField(source="profile.role", allow_null=True)

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "first_name", "last_name",
            "student_id", "lecturer_id", "profile_image", "full_name",
            "role", "display_name", "theme_preference"
        ]

    def get_profile_image(self, obj):
        return obj.profile.picture.url if hasattr(obj, "profile") and obj.profile.picture else None

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
        identifier = attrs.get("identifier")
        password = attrs.get("password")

        # Find user by email, username, student_id, or lecturer_id
        user = User.objects.filter(
            models.Q(email=identifier) |
            models.Q(username=identifier) |
            models.Q(student_id=identifier) |
            models.Q(lecturer_id=identifier)
        ).first()

        if not user:
            raise serializers.ValidationError({"identifier": "No user found with this identifier."})

        # Authenticate using the user's email
        user = authenticate(email=user.email, password=password)
        if not user:
            raise serializers.ValidationError({"non_field_errors": ["Invalid credentials."]})

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        data = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": UserSerializer(user, context=self.context).data,
            "role": user.profile.role if hasattr(user, "profile") else user.role
        }
        return data

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