from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from .utils import generate_student_id, generate_lecturer_id
from cloudinary_storage.storage import MediaCloudinaryStorage, VideoMediaCloudinaryStorage
from cloudinary_storage.validators import validate_video

class Roles(models.TextChoices):
    ADMIN = 'ADMIN', 'Admin'
    LECTURER = 'LECTURER', 'Lecturer'
    STUDENT = 'STUDENT', 'Student'

class User(AbstractUser):
    email = models.EmailField(unique=True, blank=False, null=False)
    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.STUDENT)
    student_id = models.CharField(max_length=32, blank=True, null=True, unique=True, editable=False)
    lecturer_id = models.CharField(max_length=32, blank=True, null=True, unique=True, editable=False)
    display_name = models.CharField(max_length=100, blank=True)
    theme_preference = models.CharField(max_length=10, default='light')  # 'light' or 'dark'
    profile_image = models.ImageField(
        upload_to='user_profiles/',
        blank=True,
        null=True,
        storage=MediaCloudinaryStorage(),
        help_text="Upload a profile image (optional)"
    )
    intro_video = models.FileField(
        upload_to='user_videos/',
        blank=True,
        null=True,
        storage=VideoMediaCloudinaryStorage(),
        validators=[validate_video],
        help_text="Upload an intro video (optional)"
    )

    def clean(self):
        if not self._state.adding:
            if self.role == Roles.STUDENT and not self.student_id:
                raise ValidationError('Student must have student_id')
            if self.role == Roles.LECTURER and not self.lecturer_id:
                raise ValidationError('Lecturer must have lecturer_id')

    def save(self, *args, **kwargs):
        if not self.is_superuser and not self.is_staff:
            if self.role == Roles.STUDENT and not self.student_id:
                self.student_id = generate_student_id(User)
            elif self.role == Roles.LECTURER and not self.lecturer_id:
                self.lecturer_id = generate_lecturer_id(User)
        super().save(*args, **kwargs)

    def get_initial_avatar(self):
        """Return the first letter of the display_name or username if no profile_image."""
        if self.profile_image:
            return self.profile_image.url
        name = self.display_name or self.username
        return f"{name[0].upper()}" if name else "U"  # Default to 'U' if no name

    def __str__(self):
        return f"{self.username} ({self.role})"