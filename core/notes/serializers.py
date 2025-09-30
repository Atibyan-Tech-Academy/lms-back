# notes/serializers.py
from rest_framework import serializers
from .models import Note

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = [
            "id", "user", "title", "content", "color", "pos_x", "pos_y",
            "width", "height", "z_index", "pinned", "archived",
            "created_at", "updated_at"
        ]
<<<<<<< Updated upstream
        read_only_fields = ["id", "user", "created_at", "updated_at"]
=======
        read_only_fields = ["id", "user", "created_at", "updated_at"]
>>>>>>> Stashed changes
