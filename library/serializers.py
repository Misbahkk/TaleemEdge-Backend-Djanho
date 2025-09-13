# library/serializers.py
from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User

class BookSerializer(serializers.ModelSerializer):
    is_read = serializers.SerializerMethodField()
    is_downloaded = serializers.SerializerMethodField()
    reading_progress = serializers.SerializerMethodField()
    
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'description', 'category', 'pages', 
                 'publish_year', 'isbn','file_size', 'language', 'pdf_file', 'cover_image', 'status', 
                 'download_count', 'read_count', 'created_at', 'is_read', 
                 'is_downloaded', 'reading_progress']
    
    def get_is_read(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return StudentBookActivity.objects.filter(
                user=request.user, 
                book=obj, 
                activity_type='read'
            ).exists()
        return False
    
    def get_is_downloaded(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return StudentBookActivity.objects.filter(
                user=request.user, 
                book=obj, 
                activity_type='download'
            ).exists()
        return False
    
    def get_reading_progress(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                progress = ReadingProgress.objects.get(user=request.user, book=obj)
                return {
                    'percentage': progress.progress_percentage,
                    'last_page': progress.last_page_read,
                    'is_completed': progress.is_completed,
                    'last_read_at': progress.last_read_at
                }
            except ReadingProgress.DoesNotExist:
                return None
        return None

class StudentBookActivitySerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    book_author = serializers.CharField(source='book.author', read_only=True)
    
    class Meta:
        model = StudentBookActivity
        fields = ['id', 'book', 'book_title', 'book_author', 'activity_type', 'timestamp']

class ReadingProgressSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    book_author = serializers.CharField(source='book.author', read_only=True)
    book_pages = serializers.IntegerField(source='book.pages', read_only=True)
    
    class Meta:
        model = ReadingProgress
        fields = ['id', 'book', 'book_title', 'book_author', 'book_pages',
                 'progress_percentage', 'last_page_read', 'started_at', 
                 'last_read_at', 'is_completed']

class StudentDashboardSerializer(serializers.Serializer):
    total_books_read = serializers.IntegerField()
    total_books_downloaded = serializers.IntegerField()
    currently_reading = serializers.IntegerField()
    completed_books = serializers.IntegerField()
    recent_activities = StudentBookActivitySerializer(many=True)
    reading_progress = ReadingProgressSerializer(many=True)
