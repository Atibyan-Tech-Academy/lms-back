from django.db import models
from django.conf import settings
from courses.models import Course

User = settings.AUTH_USER_MODEL


class Certificate(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'STUDENT'})
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    issued_at = models.DateTimeField(auto_now_add=True)
    certificate_file = models.FileField(upload_to='certificates/', blank=True, null=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"Certificate: {self.student.username} - {self.course.title}"
