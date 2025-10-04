# public_announcements/admin.py
from django.contrib import admin
from .models import PublicAnnouncement

@admin.register(PublicAnnouncement)
class PublicAnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_date', 'created_at']
    list_filter = ['event_date', 'created_at']
    search_fields = ['title', 'content']