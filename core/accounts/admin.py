from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email", "display_name")}),
        ("Preferences", {"fields": ("theme_preference",)}),
        ("Role & IDs", {"fields": ("role",)}),
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

    readonly_fields = ("student_id", "lecturer_id")

    def get_fields(self, request, obj=None):
        """Show only relevant fields dynamically."""
        fields = super().get_fields(request, obj)
        if obj:
            if obj.role == User.Roles.STUDENT:
                return [f for f in fields if f != "lecturer_id"]
            elif obj.role == User.Roles.LECTURER:
                return [f for f in fields if f != "student_id"]
            else:  # Admin role
                return [f for f in fields if f not in ("student_id", "lecturer_id")]
        return fields