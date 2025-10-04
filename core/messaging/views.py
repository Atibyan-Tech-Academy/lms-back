from rest_framework import generics, permissions
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer

class ConversationListCreateView(generics.ListCreateAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(participants=self.request.user)

    def perform_create(self, serializer):
        conv = serializer.save()
        conv.participants.add(self.request.user)


class MessageListCreateView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        conv_id = self.kwargs["conv_id"]
        return Message.objects.filter(conversation_id=conv_id)

    def perform_create(self, serializer):
        conv_id = self.kwargs["conv_id"]
        serializer.save(sender=self.request.user, conversation_id=conv_id)
