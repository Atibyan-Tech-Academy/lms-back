# public_announcements/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PublicAnnouncementViewSet

router = DefaultRouter()
router.register(r'', PublicAnnouncementViewSet)

urlpatterns = [
    path('', include(router.urls)),
]