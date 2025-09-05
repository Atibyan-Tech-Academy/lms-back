from rest_framework import serializers
from django.contrib.auth import authenticate
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


# Custom Login Serializer
class CustomTokenObtainSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        identifier = attrs.get("identifier")
        password = attrs.get("password")

        user = None
        try:
            user = User.objects.get(email=identifier)
        except User.DoesNotExist:
            try:
                user = User.objects.get(student_id=identifier)
            except User.DoesNotExist:
                try:
                    user = User.objects.get(lecturer_id=identifier)
                except User.DoesNotExist:
                    try:
                        user = User.objects.get(username=identifier)
                    except User.DoesNotExist:
                        pass

        if user is None:
            raise serializers.ValidationError("Invalid identifier")

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid password")

        attrs["user"] = user
        return attrs
