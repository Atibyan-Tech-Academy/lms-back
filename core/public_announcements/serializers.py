# public_announcements/serializers.py
from rest_framework import serializers
from .models import PublicAnnouncement

class PublicAnnouncementSerializer(serializers.ModelSerializer):
    post_date = serializers.SerializerMethodField()

    class Meta:
        model = PublicAnnouncement
        fields = ['id', 'title', 'content', 'image', 'event_date', 'created_at', 'post_date', 'updated_at']
        read_only_fields = ['created_at', 'post_date', 'updated_at']

    def get_post_date(self, obj):
        return obj.get_post_date() if obj.created_at else None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.image and hasattr(instance.image, 'url'):
            representation['image'] = instance.image.url  # Use Cloudinary URL
        elif instance.image:  # Handle cases where URL might not be directly accessible
            representation['image'] = f"https://res.cloudinary.com/denae5qsw/image/upload/{instance.image.public_id}"
        return representation