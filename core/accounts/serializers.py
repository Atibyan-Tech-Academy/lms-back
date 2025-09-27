from rest_framework import serializers
from django.db.models import Q
from .models import User, Roles


class UserSerializer(serializers.ModelSerializer):
    initials = serializers.SerializerMethodField()

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
            "profile_image",
            "initials",
        ]
        read_only_fields = ["student_id", "lecturer_id"]

    def get_initials(self, obj):
        return obj.get_initials() if hasattr(obj, "get_initials") else (
            f"{obj.first_name[:1]}{obj.last_name[:1]}".upper()
            if obj.first_name and obj.last_name else obj.username[:2].upper()
        )


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "role"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        role = validated_data.get("role", Roles.STUDENT)
        user = User.objects.create_user(password=password, role=role, **validated_data)
        return user


class CustomTokenObtainSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        identifier = attrs.get("identifier", "").strip()
        password = attrs.get("password")

        try:
            user = User.objects.get(
                Q(username__iexact=identifier) |
                Q(email__iexact=identifier) |
                Q(student_id__iexact=identifier) |
                Q(lecturer_id__iexact=identifier)
            )
        except User.DoesNotExist:
            raise serializers.ValidationError({"identifier": "Invalid identifier"})

        if not user.check_password(password):
            raise serializers.ValidationError({"password": "Invalid password"})

        attrs["user"] = user
        return attrs
