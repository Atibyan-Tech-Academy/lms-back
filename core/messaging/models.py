from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatRoom(models.Model):
    name = models.CharField(max_length=255, blank=True)  # Blank for one-on-one
    participants = models.ManyToManyField(User, related_name="chat_rooms")
    created_at = models.DateTimeField(auto_now_add=True)
    is_one_on_one = models.BooleanField(default=False)  # True for individual chats

    def __str__(self):
        if self.is_one_on_one:
            participants = self.participants.all()
            return f"Chat between {participants[0]} and {participants[1]}" if participants else "One-on-One Chat"
        return self.name or "Unnamed Room"

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages", null=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read_by = models.ManyToManyField(User, related_name="read_messages", blank=True)

    def __str__(self):
        return f"{self.sender} in {self.room}: {self.content[:50]}"