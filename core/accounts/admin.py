from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Roles


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email", "display_name")}),
        ("Preferences", {"fields": ("theme_preference",)}),
        ("Role & IDs", {"fields": ("role", "student_id", "lecturer_id")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "password1", "password2", "role"),
        }),
    )

    list_display = ("username", "email", "role", "student_id", "lecturer_id", "is_staff")
    list_filter = ("role", "is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("username", "email", "student_id", "lecturer_id")
    ordering = ("username",)

    def get_readonly_fields(self, request, obj=None):
        """Make IDs readonly (cannot be edited manually)."""
        if obj:
            if obj.role == Roles.STUDENT:
                return ("student_id",)
            elif obj.role == Roles.INSTRUCTOR:
                return ("lecturer_id",)
        return ()

    def get_fields(self, request, obj=None):
        """Show only the relevant ID field based on role."""
        fields = super().get_fields(request, obj)
        if obj:
            if obj.role == Roles.STUDENT:
                fields = [f for f in fields if f != "lecturer_id"]
            elif obj.role == Roles.INSTRUCTOR:
                fields = [f for f in fields if f != "student_id"]
            else:  # ADMIN role
                fields = [f for f in fields if f not in ("student_id", "lecturer_id")]
        return fields