# library/models.py
from django.db import models
from django.conf import settings

User= settings.AUTH_USER_MODEL
class Book(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('unavailable', 'Unavailable'),
    ]
    
    CATEGORY_CHOICES = [
        ('computer_science', 'Computer Science'),
        ('business', 'Business'),
        ('mathematics', 'Mathematics'),
        ('physics', 'Physics'),
        ('chemistry', 'Chemistry'),
        ('biology', 'Biology'),
        ('engineering', 'Engineering'),
        ('literature', 'Literature'),
        ('history', 'History'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    pages = models.IntegerField()
    publish_year = models.IntegerField()
    isbn = models.CharField(max_length=100)
    file_size = models.CharField(max_length=50,blank=True,null=True)
    language = models.CharField(max_length=50, default='English')
    pdf_file = models.FileField(upload_to='books/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='books/covers/', blank=True, null=True) 
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    download_count = models.IntegerField(default=0)
    read_count = models.IntegerField(default=0)  # New field for tracking reads
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']

class StudentBookActivity(models.Model):
    ACTIVITY_TYPES = [
        ('read', 'Read'),
        ('download', 'Download'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'book', 'activity_type']
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} {self.activity_type} {self.book.title}"

class ReadingProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    progress_percentage = models.FloatField(default=0.0)
    last_page_read = models.IntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    last_read_at = models.DateTimeField(auto_now=True)
    is_completed = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['user', 'book']
        ordering = ['-last_read_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.book.title} ({self.progress_percentage}%)"
