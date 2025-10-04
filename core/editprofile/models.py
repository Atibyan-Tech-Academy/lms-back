from django.db import models
from django.conf import settings

class Role(models.TextChoices):
    ADMIN = 'ADMIN', 'Admin'
    INSTRUCTOR = 'INSTRUCTOR', 'Instructor'
    STUDENT = 'STUDENT', 'Student'

class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    full_name = models.CharField(max_length=255, blank=True, null=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    department = models.CharField(max_length=100, blank=True, null=True)
    picture = models.ImageField(upload_to="profile_pictures/", blank=True, null=True)

    def __str__(self):
        return self.full_name or self.user.username
