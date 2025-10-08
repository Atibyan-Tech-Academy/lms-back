from rest_framework import serializers
from .models import User, PasswordResetCode, Roles
from editprofile.models import UserProfile
from django.utils import timezone

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
    role = serializers.ChoiceField(choices=Roles.choices, required=True)  # ✅ changed here

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
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
        serializer = TokenObtainPairSerializer(
            username_field="email",
            username=attrs["email"],
            password=attrs["password"],
        )
        data = serializer.validate(attrs)
        data["user"] = serializer.user
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
            reset_code = PasswordResetCode.objects.get(
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
            reset_code = PasswordResetCode.objects.get(
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
