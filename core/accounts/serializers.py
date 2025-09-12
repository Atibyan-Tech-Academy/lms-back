from rest_framework import serializers
from django.db.models import Q
from .models import User, Roles

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "display_name",
            "role",
            "student_id",
            "lecturer_id",
            "theme_preference",
        ]
        read_only_fields = ["student_id", "lecturer_id"]

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "role"]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            role=validated_data.get("role", Roles.STUDENT),
        )
        return user

class CustomTokenObtainSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        identifier = attrs.get("identifier").strip()
        password = attrs.get("password")

        print(f"Received login attempt: identifier='{identifier}'")  # Debug
        try:
            user = User.objects.get(
                Q(username__iexact=identifier) |
                Q(email__iexact=identifier) |
                Q(student_id__iexact=identifier) |
                Q(lecturer_id__iexact=identifier)
            )
        except User.DoesNotExist:
            print(f"Login failed: No user found for identifier '{identifier}'")
            raise serializers.ValidationError("Invalid identifier")

        if not user.check_password(password):
            print(f"Login failed: Invalid password for user '{user.username}'")
            raise serializers.ValidationError("Invalid password")

        attrs["user"] = user
        print(f"Login successful for user '{user.username}'")
        return attrs