from django.db import models
from authentication.models import User
from django.db.models import Count

class Scholarship(models.Model):
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('expired','Expired')
    ]
    
    ACADEMIC_LEVELS = [
        ('high_school', 'High School'),
        ('undergraduate', 'Undergraduate'),
        ('graduate', 'Graduate'),
        ('all_levels', 'All Levels'),
    ]
    
    title = models.CharField(max_length=255)
    provider = models.CharField(max_length=255)
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    deadline = models.DateTimeField()
    category = models.CharField(max_length=100)
    max_applicants = models.IntegerField(blank=True, null=True)
    academic_level = models.CharField(max_length=20, choices=ACADEMIC_LEVELS)
    country = models.CharField(max_length=100)
    application_url = models.URLField()
    eligibility_criteria = models.TextField(help_text="Comma-separated values")
    requirements = models.TextField(help_text="Comma-separated values")
    benefits = models.TextField(help_text="Comma-separated values")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def total_applications(self):
        return self.applications.count()
    
    @property
    def is_full(self):
        if self.max_applicants:
            return self.total_applications >= self.max_applicants
        return False
    
    def __str__(self):
        return self.title


class ScholarshipApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('under_review', 'Under Review'),
    ]
    
    scholarship = models.ForeignKey(Scholarship, on_delete=models.CASCADE, related_name='applications')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scholarship_applications')
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True, help_text="Additional notes from student")
    admin_notes = models.TextField(blank=True, null=True, help_text="Notes from admin")
    
    class Meta:
        unique_together = ['scholarship', 'student']  # Student can only apply once per scholarship
    
    def __str__(self):
        return f"{self.student.username} - {self.scholarship.title}"


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('scholarship_application', 'Scholarship Application'),
        ('scholarship_status_update', 'Scholarship Status Update'),
        ('new_scholarship', 'New Scholarship'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    scholarship = models.ForeignKey(Scholarship, on_delete=models.CASCADE, null=True, blank=True)
    application = models.ForeignKey(ScholarshipApplication, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"


# class UserProfile(models.Model):
#     ROLE_CHOICES = [
#         ('admin', 'Admin'),
#         ('student', 'Student'),
#     ]
    
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
#     role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
#     phone = models.CharField(max_length=15, blank=True, null=True)
#     date_of_birth = models.DateField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
    
#     def __str__(self):
#         return f"{self.user.username} - {self.role}"