from rest_framework.routers import DefaultRouter
from .views import CertificateViewSet

router = DefaultRouter()
router.register(r'certificates', CertificateViewSet)

urlpatterns = router.urls
