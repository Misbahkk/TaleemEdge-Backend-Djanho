# models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import EmailValidator
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('student', 'Student'),
    ]
    
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    school_name = models.CharField(max_length=255, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to="profile_pics/",null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'username']
    
    def __str__(self):
        return self.full_name


class PlatformActivity(models.Model):
    ACTIVITY_TYPES = [
        ('user_registration', 'User Registration'),
        ('workshop_enrollment', 'Workshop Enrollment'),
        ('book_download', 'Book Downloaded'),
        ('mentor_application', 'Mentor Application'),
        ('scholarship_application', 'Scholarship Application'),
    ]
    
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    user_name = models.CharField(max_length=255)
    description = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Platform Activities"




class PlatformSettings(models.Model):
    # Basic Platform Settings
    site_name = models.CharField(max_length=255, default="Taleem Edge")
    site_description = models.TextField(default="Educational Platform")
    
    # Theme & Branding
    primary_color = models.CharField(max_length=7, default="#10B981")
    secondary_color = models.CharField(max_length=7, default="#3B82F6")
    logo = models.ImageField(upload_to='branding/', blank=True, null=True)
    favicon = models.ImageField(upload_to='branding/', blank=True, null=True)
    
    # Platform Controls
    maintenance_mode = models.BooleanField(default=False)
    allow_new_registrations = models.BooleanField(default=True)
    
    # Hero Section
    hero_title = models.CharField(max_length=255, default="Welcome to Taleem Edge")
    hero_subtitle = models.TextField(default="Your Gateway to Quality Education")
    hero_image = models.ImageField(upload_to='hero/', blank=True, null=True)
    
    # Announcement Banner
    announcement_enabled = models.BooleanField(default=False)
    announcement_text = models.TextField(blank=True)
    announcement_link = models.URLField(blank=True)
    announcement_type = models.CharField(
        max_length=20,
        choices=[('info', 'Info'), ('warning', 'Warning'), ('success', 'Success')],
        default='info'
    )
    
    # Contact Information
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    contact_address = models.TextField(blank=True)
    
    # Social Media Links
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Platform Settings"
        verbose_name_plural = "Platform Settings"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and PlatformSettings.objects.exists():
            raise ValueError('There can be only one PlatformSettings instance')
        return super(PlatformSettings, self).save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        settings, created = cls.objects.get_or_create(pk=1)
        return settings
    

    