from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from .models import Course, Material, Enrollment, Module, StudentProgress, Announcement
from .serializers import (
    CourseSerializer, MaterialSerializer, EnrollmentSerializer,
    ModuleSerializer, StudentProgressSerializer, AnnouncementSerializer
)

class IsAdminOrInstructor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_staff or request.user.role == "LECTURER"  # Fixed
        )

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Course.objects.all()
        elif user.role == "LECTURER":  # Fixed
            return Course.objects.filter(instructor=user)
        elif user.role == "STUDENT":
            return Course.objects.filter(enrollments__student=user)
        return Course.objects.none()

class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = [IsAdminOrInstructor]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Module.objects.all()
        return Module.objects.filter(course__instructor=user)

    def perform_create(self, serializer):
        course_id = self.request.data.get("course")
        serializer.save(course_id=course_id)

class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    permission_classes = [IsAdminOrInstructor]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Material.objects.all()
        return Material.objects.filter(module__course__instructor=user)

    def perform_create(self, serializer):
        module_id = self.request.data.get("module")
        serializer.save(module_id=module_id)

class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Enrollment.objects.all()
        elif user.role == "LECTURER":  # Fixed
            return Enrollment.objects.filter(course__instructor=user)
        return Enrollment.objects.filter(student=user)

    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_staff:
            raise permissions.PermissionDenied("Only admin can assign courses.")
        serializer.save()

class StudentProgressViewSet(viewsets.ModelViewSet):
    queryset = StudentProgress.objects.all()
    serializer_class = StudentProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return StudentProgress.objects.all()
        elif user.role == "LECTURER":  # Fixed
            return StudentProgress.objects.filter(module__course__instructor=user)
        return StudentProgress.objects.filter(student=user)

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
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [IsAdminOrInstructor()]

    def perform_create(self, serializer):
        course_id = self.request.data.get("course")
        serializer.save(course_id=course_id)

class InstructorDashboardView(APIView):
    permission_classes = [IsAdminOrInstructor]

    def get(self, request):
        user = request.user
        if not (user.is_staff or user.role == "LECTURER"):  # Fixed
            return Response({"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)

        courses = Course.objects.filter(instructor=user)
        total_courses = courses.count()
        total_enrollments = Enrollment.objects.filter(course__instructor=user).count()
        recent_enrollments = Enrollment.objects.filter(
            course__instructor=user
        ).order_by("-enrolled_at")[:5]
        recent_enrollments_data = [
            {
                "student": e.student.username,
                "course": e.course.title,
                "enrolled_at": e.enrolled_at,
            }
            for e in recent_enrollments
        ]
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

class StudentDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.is_staff or user.role == "LECTURER":  # Fixed
            return Response({"detail": "Not authorized as student"}, status=status.HTTP_403_FORBIDDEN)

        enrollments = Enrollment.objects.filter(student=user).select_related("course")
        enrolled_courses = [
            {
                "course_id": e.course.id,
                "course_title": e.course.title,
                "description": e.course.description,
                "instructor": e.course.instructor.username if e.course.instructor else None,
            }
            for e in enrollments
        ]
        progress = StudentProgress.objects.filter(student=user)
        progress_data = [
            {
                "module": p.module.title,
                "course": p.module.course.title,
                "completed": p.completed,
                "last_accessed": p.updated_at,  # Fixed: align with model field
            }
            for p in progress
        ]
        announcements = Announcement.objects.filter(course__enrollments__student=user).order_by("-created_at")[:5]
        announcement_data = [
            {
                "course": a.course.title if a.course else "General",
                "title": a.title,
                "content": a.content,  # Fixed: changed from message
                "created_at": a.created_at,
            }
            for a in announcements
        ]

        data = {
            "student": user.username,
            "enrolled_courses": enrolled_courses,
            "progress": progress_data,
            "announcements": announcement_data,
        }
        return Response(data, status=status.HTTP_200_OK)