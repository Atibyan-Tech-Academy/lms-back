# courses/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from .models import Course, Material, Enrollment, Module, StudentProgress, Announcement
from .serializers import (
    CourseSerializer, MaterialSerializer, EnrollmentSerializer,
    ModuleSerializer, StudentProgressSerializer, AnnouncementSerializer
)

# Updated permission class
class IsAdminOrInstructor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.is_staff or request.user.role in ["INSTRUCTOR", "LECTURER"])

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Course.objects.all()
        if self.request.user.role in ["INSTRUCTOR", "LECTURER"]:
            return Course.objects.filter(instructor=self.request.user)
        return Course.objects.filter(enrollments__student=self.request.user)

class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = [IsAdminOrInstructor]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Module.objects.all()
        return Module.objects.filter(course__instructor=self.request.user)

    def perform_create(self, serializer):
        serializer.save(course_id=self.request.data.get('course'))

class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    permission_classes = [IsAdminOrInstructor]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Material.objects.all()
        return Material.objects.filter(module__course__instructor=self.request.user)

    def perform_create(self, serializer):
        serializer.save(module_id=self.request.data.get('module'))

class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Enrollment.objects.all()
        return Enrollment.objects.filter(student=self.request.user)

class StudentProgressViewSet(viewsets.ModelViewSet):
    queryset = StudentProgress.objects.all()
    serializer_class = StudentProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return StudentProgress.objects.all()
        return StudentProgress.objects.filter(student=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(student=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:  # Allow public read access
            return [permissions.AllowAny()]
        return [IsAdminOrInstructor()]  # Restrict create/update/delete to instructors/admins

    def perform_create(self, serializer):
        serializer.save(course_id=self.request.data.get('course'))

# Fixed InstructorDashboardView to include LECTURER role
class InstructorDashboardView(APIView):
    permission_classes = [IsAdminOrInstructor]

    def get(self, request):
        user = request.user
        if not user.is_staff and user.role not in ["INSTRUCTOR", "LECTURER"]:
            return Response({"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)

        # Fetch instructor’s courses
        courses = Course.objects.filter(instructor=user)
        total_courses = courses.count()

        # Total enrollments across all courses
        total_enrollments = Enrollment.objects.filter(course__instructor=user).count()

        # Latest 5 enrollments
        recent_enrollments = Enrollment.objects.filter(course__instructor=user).order_by("-enrolled_at")[:5]
        recent_enrollments_data = [
            {
                "student": e.student.username,
                "course": e.course.title,
                "enrolled_at": e.enrolled_at,
            }
            for e in recent_enrollments
        ]

        # Student progress summary
        progress = StudentProgress.objects.filter(module__course__instructor=user)
        completed_count = progress.filter(completed=True).count()
        in_progress_count = progress.filter(completed=False).count()

        data = {
            "total_courses": total_courses,
            "total_enrollments": total_enrollments,
            "completed_lessons": completed_count,
            "in_progress_lessons": in_progress_count,
            "recent_enrollments": recent_enrollments_data,
        }
        return Response(data, status=status.HTTP_200_OK)
