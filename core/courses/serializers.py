from rest_framework import serializers
from .models import Course, Module, Material, Enrollment, StudentProgress, Announcement


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ["id", "title", "file", "video", "video_url", "uploaded_at"]


class ModuleSerializer(serializers.ModelSerializer):
    materials = MaterialSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = ["id", "title", "order", "materials"]


class CourseSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)
    instructor_name = serializers.CharField(source="instructor.username", read_only=True)

    class Meta:
        model = Course
        fields = ["id", "title", "description", "instructor_name", "created_at", "modules"]


class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(),
        source="course",
        write_only=True
    )

    class Meta:
        model = Enrollment
        fields = ["id", "course", "course_id", "enrolled_at"]


class StudentProgressSerializer(serializers.ModelSerializer):
    module_title = serializers.CharField(source="module.title", read_only=True)

    class Meta:
        model = StudentProgress
        fields = ["id", "module", "module_title", "completed", "updated_at"]


class AnnouncementSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title", read_only=True)

    class Meta:
        model = Announcement
        fields = ["id", "title", "content", "created_at", "course_title"]
