# admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import HeroSection, FeatureCard

@admin.register(HeroSection)
class HeroSectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'video_preview', 'image_preview', 'updated_at']
    list_editable = ['is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'subtitle', 'heading']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'subtitle', 'heading', 'description')
        }),
        ('Media Files', {
            'fields': ('hero_video', 'hero_image', 'video_poster'),
            'description': 'Upload video, image, and video poster'
        }),
        ('Statistics', {
            'fields': ('rating', 'total_students', 'total_resources')
        }),
        ('Call to Action Buttons', {
            'fields': ('primary_button_text', 'primary_button_link', 
                      'secondary_button_text', 'secondary_button_link')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    def video_preview(self, obj):
        if obj.hero_video:
            return format_html(
                '<video width="100" height="60" controls>'
                '<source src="{}" type="video/mp4">'
                '</video>',
                obj.hero_video.url
            )
        return "No Video"
    video_preview.short_description = "Video Preview"
    
    def image_preview(self, obj):
        if obj.hero_image:
            return format_html(
                '<img src="{}" width="100" height="60" style="object-fit: cover;" />',
                obj.hero_image.url
            )
        return "No Image"
    image_preview.short_description = "Image Preview"
    
    # Limit to only one hero section
    def has_add_permission(self, request):
        if HeroSection.objects.exists():
            return False
        return True

@admin.register(FeatureCard)
class FeatureCardAdmin(admin.ModelAdmin):
    list_display = ['title', 'icon', 'color', 'order', 'is_active']
    list_editable = ['order', 'is_active', 'color']
    list_filter = ['color', 'icon', 'is_active']
    search_fields = ['title', 'description']
    ordering = ['order']
    
    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_active=True)