from rest_framework import serializers
from .models import ChatRoom, Message
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']  # Add fields as needed (e.g., role)

class ChatRoomSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    participants = UserSerializer(many=True)

    class Meta:
        model = ChatRoom
        fields = ["id", "name", "participants", "last_message", "is_one_on_one"]

    def get_last_message(self, obj):
        message = obj.messages.order_by("-timestamp").first()
        return MessageSerializer(message).data if message else None

class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField()
    read_by = serializers.StringRelatedField(many=True)
    room = serializers.PrimaryKeyRelatedField(queryset=ChatRoom.objects.all())

    class Meta:
        model = Message
        fields = ["id", "room", "sender", "content", "timestamp", "read_by"]