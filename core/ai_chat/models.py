from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class AIChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ai_messages")
    sender = models.CharField(max_length=10, choices=[("user", "User"), ("ai", "AI")])
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.user} ({self.sender}): {self.text[:30]}"
