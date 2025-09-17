from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, MaterialViewSet, EnrollmentViewSet, ModuleViewSet, StudentProgressViewSet, AnnouncementViewSet

router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'materials', MaterialViewSet)
router.register(r'enrollments', EnrollmentViewSet)
router.register(r'modules', ModuleViewSet)
router.register(r'progress', StudentProgressViewSet)
router.register(r'announcements', AnnouncementViewSet)

urlpatterns = router.urls