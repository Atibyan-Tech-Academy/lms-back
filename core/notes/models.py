from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

class Note(models.Model):
    COLOR_CHOICES = (
        ('yellow', 'Yellow'),
        ('pink', 'Pink'),
        ('green', 'Green'),
        ('blue', 'Blue'),
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notes"
    )
    title = models.CharField(max_length=100)
    content = models.TextField()
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, default='yellow')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.student.username}"

    def clean(self):
        if self.student.profile.role != "STUDENT":
            raise ValidationError("Only students can create notes.")