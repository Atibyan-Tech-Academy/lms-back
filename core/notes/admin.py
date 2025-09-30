from django.contrib import admin
<<<<<<< Updated upstream
from .models import Note

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ("id","user","title","pinned","created_at")
    list_filter = ("pinned","archived")
    search_fields = ("title","content","user__username","user__email")
=======

# Register your models here.
>>>>>>> Stashed changes
