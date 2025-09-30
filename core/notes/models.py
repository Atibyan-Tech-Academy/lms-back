# notes/models.py
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notes")
    title = models.CharField(max_length=255, blank=True)
    content = models.TextField(blank=True)
<<<<<<< Updated upstream
<<<<<<< Updated upstream
    color = models.CharField(max_length=7, default="#FFF9C4")  # default sticky color
=======
    color = models.CharField(max_length=7, default="#FFFFFF")  # default sticky color
>>>>>>> Stashed changes
=======
    color = models.CharField(max_length=7, default="#FFFFFF")  # default sticky color
>>>>>>> Stashed changes
    pos_x = models.IntegerField(default=0)
    pos_y = models.IntegerField(default=0)
    width = models.IntegerField(default=260)
    height = models.IntegerField(default=180)
    z_index = models.IntegerField(default=0)
    pinned = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-pinned", "-updated_at"]

<<<<<<< Updated upstream
    def __str__(self):
        return f"{self.title or 'Note'} ({self.user})"
=======
    def _str_(self):
        return f"{self.title or 'Note'} ({self.user})"
>>>>>>> Stashed changes
