from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserProfileViewSet

router = DefaultRouter()
router.register(r"", UserProfileViewSet, basename="editprofile")

urlpatterns = [
    path("", include(router.urls)),
    path("profile/", UserProfileViewSet.as_view({"get": "profile", "put": "profile"}), name="profile"),
]