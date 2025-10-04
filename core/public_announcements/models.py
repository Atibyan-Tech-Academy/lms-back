# public_announcements/models.py
from django.db import models
from cloudinary.models import CloudinaryField

class PublicAnnouncement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = CloudinaryField(resource_type="image", blank=True, null=True)
    event_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-event_date', '-created_at']

    def __str__(self):
        return f"{self.title} - {self.event_date}"

    def get_post_date(self):
        return self.created_at.date()