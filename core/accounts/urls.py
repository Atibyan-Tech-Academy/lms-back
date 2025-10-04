from django.urls import path
from .views import RegisterView, ProfileView, CustomLoginView, GetCSRFToken
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", CustomLoginView.as_view(), name="custom-login"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("get-csrf-token/", GetCSRFToken.as_view(), name="get-csrf-token"),
]