# models.py
from django.db import models
from authentication.models import User

# class User(AbstractUser):
#     ROLE_CHOICES = [
#         ('admin', 'Admin'),
#         ('student', 'Student'),
#     ]
#     role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')

class Video(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=100)
    youtube_video_id = models.CharField(max_length=50, unique=True)
    duration = models.CharField(max_length=20)
    views = models.CharField(max_length=20, default='0')
    thumbnail_url = models.URLField(blank=True, null=True)  # Manual thumbnail URL
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    @property
    def youtube_url(self):
        return f"https://www.youtube.com/watch?v={self.youtube_video_id}"
    
    @property
    def youtube_embed_url(self):
        return f"https://www.youtube.com/embed/{self.youtube_video_id}"
    
    class Meta:
        ordering = ['-created_at']

