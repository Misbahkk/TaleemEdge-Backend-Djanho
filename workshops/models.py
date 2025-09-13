# workshops/models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Workshop(models.Model):
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    LOCATION_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline'),
    ]
    
    title = models.CharField(max_length=255)
    instructor = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    duration = models.CharField(max_length=50)
    capacity = models.IntegerField()
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    category = models.CharField(max_length=100)
    location = models.CharField(max_length=20, choices=LOCATION_CHOICES)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    enrolled_count = models.IntegerField(default=0)
    
    # Media fields for admin
    main_image = models.ImageField(upload_to='workshop_images/', null=True, blank=True)
    video = models.FileField(upload_to='workshop_videos/', null=True, blank=True)
    
    # Admin who created the workshop
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_workshops')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

class WorkshopEnrollment(models.Model):
    """Model to track workshop enrollments"""
    workshop = models.ForeignKey(Workshop, on_delete=models.CASCADE, related_name='enrollments')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workshop_enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('workshop', 'student')  # Prevent duplicate enrollments
        ordering = ['-enrolled_at']
    
    def __str__(self):
        return f"{self.student.full_name} - {self.workshop.title}"
    

    