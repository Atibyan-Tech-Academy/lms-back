from django.db import models
from django.conf import settings
from courses.models import Course

User = settings.AUTH_USER_MODEL


class Assignment(models.Model):
    course = models.ForeignKey(Course, related_name="assignments", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.course.title})"


class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, related_name="submissions", on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={"role": "STUDENT"})
    file = models.FileField(upload_to="submissions/", blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    grade = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    feedback = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ("assignment", "student")  # one submission per student

    def __str__(self):
        return f"{self.student} - {self.assignment.title}"
