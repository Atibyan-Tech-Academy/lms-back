
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CourseViewSet, ModuleViewSet, MaterialViewSet,
    EnrollmentViewSet, StudentProgressViewSet, AnnouncementViewSet,
    InstructorDashboardView, StudentDashboardView
)

# Router for standard CRUD endpoints
router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'modules', ModuleViewSet, basename='module')
router.register(r'materials', MaterialViewSet, basename='material')
router.register(r'enrollments', EnrollmentViewSet, basename='enrollment')
router.register(r'progress', StudentProgressViewSet, basename='progress')
router.register(r'announcements', AnnouncementViewSet, basename='announcement')

urlpatterns = [
    path('', include(router.urls)),

    # Custom dashboards
    path('instructor/dashboard/', InstructorDashboardView.as_view(), name='instructor-dashboard'),
    path('student/dashboard/', StudentDashboardView.as_view(), name='student-dashboard'),
]

