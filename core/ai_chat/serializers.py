from rest_framework import serializers
from .models import AIChatMessage

class AIChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIChatMessage
        fields = ["id", "user", "sender", "text", "created_at"]
        read_only_fields = ["user", "created_at"]
