from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from .utils import generate_student_id, generate_lecturer_id


class Roles(models.TextChoices):
    ADMIN = 'ADMIN', 'Admin'
    LECTURER = 'LECTURER', 'Lecturer'   # ✅ consistent
    STUDENT = 'STUDENT', 'Student'


class User(AbstractUser):
    email = models.EmailField(unique=True, blank=False, null=False)
    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.STUDENT)
    student_id = models.CharField(max_length=32, blank=True, null=True, unique=True, editable=False)
    lecturer_id = models.CharField(max_length=32, blank=True, null=True, unique=True, editable=False)
    display_name = models.CharField(max_length=100, blank=True)
    theme_preference = models.CharField(max_length=10, default='light')  # 'light' or 'dark'

    def clean(self):
        # Prevent tampering after creation
        if not self._state.adding:
            if self.role == Roles.STUDENT and not self.student_id:
                raise ValidationError('Student must have student_id')
            if self.role == Roles.LECTURER and not self.lecturer_id:
                raise ValidationError('Lecturer must have lecturer_id')

    def save(self, *args, **kwargs):
        # Skip ID generation for superusers and staff
        if not self.is_superuser and not self.is_staff:
            if self.role == Roles.STUDENT and not self.student_id:
                self.student_id = generate_student_id(User)
            elif self.role == Roles.LECTURER and not self.lecturer_id:
                self.lecturer_id = generate_lecturer_id(User)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.role})"
