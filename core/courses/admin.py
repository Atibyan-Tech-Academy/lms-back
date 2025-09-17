from django.contrib import admin
from .models import Course, Material, Enrollment, Module, StudentProgress, Announcement

admin.site.register(Course)
admin.site.register(Material)
admin.site.register(Enrollment)
admin.site.register(Module)
admin.site.register(StudentProgress)
admin.site.register(Announcement)