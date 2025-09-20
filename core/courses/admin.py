from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Course, Module, Material, Enrollment, StudentProgress, Announcement


class MaterialAdmin(admin.ModelAdmin):
    list_display = ("title", "module", "uploaded_at", "video_preview")

    readonly_fields = ("video_preview",)

    def video_preview(self, obj):
        """Show embedded YouTube preview in admin if URL exists"""
        if obj.video_url:
            # Extract the video ID from YouTube link
            if "watch?v=" in obj.video_url:
                video_id = obj.video_url.split("watch?v=")[-1]
            elif "youtu.be/" in obj.video_url:
                video_id = obj.video_url.split("youtu.be/")[-1]
            else:
                return "Invalid YouTube URL"

            embed_url = f"https://www.youtube.com/embed/{video_id}"
            return mark_safe(
                f'<iframe width="320" height="180" src="{embed_url}" frameborder="0" allowfullscreen></iframe>'
            )
        return "No video"

    video_preview.short_description = "YouTube Preview"


# Register models
admin.site.register(Course)
admin.site.register(Module)
admin.site.register(Material, MaterialAdmin)
admin.site.register(Enrollment)
admin.site.register(StudentProgress)
admin.site.register(Announcement)
