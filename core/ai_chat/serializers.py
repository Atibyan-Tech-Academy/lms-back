from rest_framework import serializers
from .models import AIChatMessage

class AIChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIChatMessage
        fields = ['id', 'user', 'message', 'is_ai_response', 'timestamp']