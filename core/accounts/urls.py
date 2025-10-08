from django.urls import path
from .views import (
    RegisterView, ProfileView, CustomLoginView, GetCSRFToken,
    PasswordResetRequestView, PasswordResetVerifyView, PasswordResetConfirmView,
    UserListView
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("get-csrf-token/", GetCSRFToken.as_view(), name="get-csrf-token"),
    path("password-reset/", PasswordResetRequestView.as_view(), name="password-reset"),
    path("password-reset-verify/", PasswordResetVerifyView.as_view(), name="password-reset-verify"),
    path("password-reset-confirm/", PasswordResetConfirmView.as_view(), name="password-reset-confirm"),
    path("users/", UserListView.as_view(), name="user-list"),
]