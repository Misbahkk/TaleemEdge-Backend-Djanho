# serializers.py
from rest_framework import serializers
from .models import BlogPost, Category

class BlogPostSerializer(serializers.ModelSerializer):
    tags_list = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'author', 'excerpt', 'content', 'read_time',
            'medium_url', 'status', 'tags', 'tags_list', 'views',
            'created_at', 'updated_at', 'published_date'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'views', 'published_date']
    
    def get_tags_list(self, obj):
        return obj.get_tags_list()

class BlogPostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = [
            'title', 'author', 'excerpt', 'content', 'read_time',
            'medium_url', 'status', 'tags'
        ]

class BlogPostListSerializer(serializers.ModelSerializer):
    tags_list = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'author', 'excerpt', 'read_time',
            'medium_url', 'status', 'tags', 'tags_list', 'views',
            'created_at', 'published_date'
        ]
    
    def get_tags_list(self, obj):
        return obj.get_tags_list()

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'created_at']
        read_only_fields = ['id', 'created_at']