# courses/urls.py
from rest_framework.routers import DefaultRouter
from .views import (
    CourseViewSet, MaterialViewSet, EnrollmentViewSet,
    ModuleViewSet, StudentProgressViewSet, AnnouncementViewSet
)
from django.urls import path
from .views import InstructorDashboardView

router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'modules', ModuleViewSet)
router.register(r'materials', MaterialViewSet)
router.register(r'enrollments', EnrollmentViewSet)
router.register(r'progress', StudentProgressViewSet)
router.register(r'announcements', AnnouncementViewSet)

urlpatterns = router.urls + [
    path("instructor/dashboard/", InstructorDashboardView.as_view(), name="instructor-dashboard"),
]