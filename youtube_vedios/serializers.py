
# serializers.py
from rest_framework import serializers
from .models import Video

class VideoSerializer(serializers.ModelSerializer):
    youtube_url = serializers.ReadOnlyField()
    youtube_embed_url = serializers.ReadOnlyField()
    
    class Meta:
        model = Video
        fields = [
            'id', 'title', 'description', 'category', 
            'youtube_video_id', 'duration', 'views', 
            'thumbnail_url', 'youtube_url', 'youtube_embed_url',
            'created_at', 'updated_at'
        ]
        
    def validate_youtube_video_id(self, value):
        # Basic validation for YouTube video ID format
        if len(value) != 11:
            raise serializers.ValidationError("Invalid YouTube video ID format")
        return value

class VideoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = [
            'title', 'description', 'category', 
            'youtube_video_id', 'duration', 'views', 'thumbnail_url'
        ]

class VideoUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = [
            'title', 'description', 'category', 
            'duration', 'views', 'thumbnail_url'
        ]

        