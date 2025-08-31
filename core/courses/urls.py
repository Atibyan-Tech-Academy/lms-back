from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, MaterialViewSet, EnrollmentViewSet

router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'materials', MaterialViewSet)
router.register(r'enrollments', EnrollmentViewSet)

urlpatterns = router.urls