from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user_email", "full_name", "role", "department")
    readonly_fields = ("role", "department")

    # Show user email in list_display
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = "Email"
