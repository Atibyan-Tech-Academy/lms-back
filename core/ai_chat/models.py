from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class AIChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ai_messages")
    message = models.TextField()
    is_ai_response = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - AI Chat: {self.message[:50]}"