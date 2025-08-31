from django.contrib import admin
from .models import Course, Material, Enrollment

admin.site.register(Course)
admin.site.register(Material)
admin.site.register(Enrollment)