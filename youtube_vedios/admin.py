# admin.py
from django.contrib import admin
from .models import Video

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'youtube_video_id', 'duration', 'views', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['title', 'description', 'category']
    readonly_fields = ['created_at', 'updated_at']


# utils.py - YouTube thumbnail helper (optional)
def get_youtube_thumbnail(video_id):
    """
    Generate YouTube thumbnail URLs
    """
    return {
        'default': f"https://img.youtube.com/vi/{video_id}/default.jpg",
        'medium': f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg",
        'high': f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
        'standard': f"https://img.youtube.com/vi/{video_id}/sddefault.jpg",
        'maxres': f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
    }