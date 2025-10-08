from django.db import models
from accounts.models import User, Roles

class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    full_name = models.CharField(max_length=255, blank=True, null=True)
    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.STUDENT)
    department = models.CharField(max_length=100, blank=True, null=True)
    picture = models.ImageField(upload_to="profile_pictures/", blank=True, null=True)

    def __str__(self):
        return self.full_name or self.user.username