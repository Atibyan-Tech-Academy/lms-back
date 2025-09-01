from rest_framework import serializers
from .models import Certificate


class CertificateSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.username", read_only=True)
    course_title = serializers.CharField(source="course.title", read_only=True)

    class Meta:
        model = Certificate
        fields = ['id', 'student', 'student_name', 'course', 'course_title', 'issued_at', 'certificate_file']