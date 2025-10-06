from django.urls import path
from .views import (
    RegisterView,
    ProfileView,
    CustomLoginView,
    GetCSRFToken,
    PasswordResetRequestView,
    PasswordResetVerifyView,
    PasswordResetConfirmView,
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", CustomLoginView.as_view(), name="custom-login"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("get-csrf-token/", GetCSRFToken.as_view(), name="get-csrf-token"),
    path("password-reset/", PasswordResetRequestView.as_view(), name="password_reset"),
    path("password-reset-verify/", PasswordResetVerifyView.as_view(), name="password_reset_verify"),
    path("password-reset-confirm/", PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
]