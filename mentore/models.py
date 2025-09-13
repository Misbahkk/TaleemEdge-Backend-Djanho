from django.db import models

# Create your models here.
class Mentor(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    job_title = models.CharField(max_length=255)
    company = models.CharField(max_length=255, blank=True)
    years_of_experience = models.IntegerField()
    bio = models.TextField()
    location = models.CharField(max_length=255)
    availability = models.CharField(max_length=255)
    expertise_areas = models.TextField(help_text="Comma-separated values")
    specializations = models.TextField(help_text="Comma-separated values")
    languages = models.TextField(help_text="Comma-separated values")
    linkedin_profile = models.URLField(blank=True)
    profile_picture = models.ImageField(upload_to='mentors/', blank=True, null=True)  # ✅ New
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.full_name
