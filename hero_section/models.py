# models.py
from django.db import models
from django.core.validators import FileExtensionValidator

class HeroSection(models.Model):
    title = models.CharField(max_length=200, default="Taleem Edge")
    subtitle = models.CharField(max_length=200, default="by Rah e Ilahi")
    heading = models.CharField(max_length=300, default="Empowering Your Learning Journey")
    description = models.TextField(default="A comprehensive learning management system...")
    
    # Video/Image fields
    hero_video = models.FileField(
        upload_to='hero_videos/',
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'webm', 'avi'])],
        null=True,
        blank=True,
        help_text="Upload hero section video"
    )
    
    hero_image = models.ImageField(
        upload_to='hero_images/',
        null=True,
        blank=True,
        help_text="Fallback image if video is not available"
    )
    
    video_poster = models.ImageField(
        upload_to='video_posters/',
        null=True,
        blank=True,
        help_text="Video thumbnail/poster image"
    )
    
    # Stats
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=4.9)
    total_students = models.CharField(max_length=50, default="10,000+")
    total_resources = models.CharField(max_length=50, default="500+")
    
    # Buttons
    primary_button_text = models.CharField(max_length=100, default="Get Started Free")
    primary_button_link = models.CharField(max_length=200, default="/auth/signup")
    secondary_button_text = models.CharField(max_length=100, default="Watch Demo")
    secondary_button_link = models.CharField(max_length=200, default="/auth/login")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Hero Section"
        verbose_name_plural = "Hero Sections"
    
    def __str__(self):
        return f"Hero Section - {self.title}"

class FeatureCard(models.Model):
    ICON_CHOICES = [
        ('users', 'Users'),
        ('book-open', 'Book Open'),
        ('message-circle', 'Message Circle'),
        ('graduation-cap', 'Graduation Cap'),
        ('star', 'Star'),
        ('play', 'Play'),
    ]
    
    COLOR_CHOICES = [
        ('green', 'Green'),
        ('blue', 'Blue'),
        ('purple', 'Purple'),
        ('red', 'Red'),
        ('yellow', 'Yellow'),
        ('indigo', 'Indigo'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.CharField(max_length=50, choices=ICON_CHOICES, default='users')
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, default='green')
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order']
        verbose_name = "Feature Card"
        verbose_name_plural = "Feature Cards"
    
    def __str__(self):
        return self.title