from rest_framework import serializers
from .models import Course, Material, Enrollment, Module, StudentProgress, Announcement


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ['id', 'title', 'file', 'video', 'video_url', 'uploaded_at']


class ModuleSerializer(serializers.ModelSerializer):
    materials = MaterialSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = ['id', 'title', 'order', 'materials']


class StudentProgressSerializer(serializers.ModelSerializer):
    module_title = serializers.CharField(source='module.title', read_only=True)

    class Meta:
        model = StudentProgress
        fields = ['id', 'student', 'module', 'module_title', 'completed', 'updated_at']


class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ['id', 'title', 'content', 'created_at', 'course']


class CourseSerializer(serializers.ModelSerializer):
    instructor_name = serializers.CharField(source="instructor.username", read_only=True)
    modules = ModuleSerializer(many=True, read_only=True)
    announcements = AnnouncementSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'instructor', 'instructor_name',
            'created_at', 'modules', 'announcements'
        ]


class EnrollmentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title", read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course', 'course_title', 'enrolled_at']
