# workshops/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Workshop, WorkshopEnrollment

@admin.register(Workshop)
class WorkshopAdmin(admin.ModelAdmin):
    list_display = ['title', 'instructor', 'date', 'time', 'level', 'category', 
                   'status', 'enrolled_count', 'capacity', 'created_by', 'image_preview']
    list_filter = ['status', 'level', 'category', 'location', 'date', 'created_by']
    search_fields = ['title', 'instructor', 'category', 'description']
    readonly_fields = ['enrolled_count', 'created_at', 'updated_at', 'image_preview', 'video_preview']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'instructor', 'description', 'category')
        }),
        ('Schedule', {
            'fields': ('date', 'time', 'duration', 'location')
        }),
        ('Details', {
            'fields': ('level', 'capacity', 'price', 'status')
        }),
        ('Media', {
            'fields': ('main_image', 'image_preview', 'video', 'video_preview')
        }),
        ('System Info', {
            'fields': ('created_by', 'enrolled_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def image_preview(self, obj):
        if obj.main_image:
            return format_html('<img src="{}" width="100" height="100" />', obj.main_image.url)
        return "No Image"
    image_preview.short_description = "Image Preview"
    
    def video_preview(self, obj):
        if obj.video:
            return format_html('<video width="200" controls><source src="{}" type="video/mp4"></video>', obj.video.url)
        return "No Video"
    video_preview.short_description = "Video Preview"
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only set created_by for new objects
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(WorkshopEnrollment)
class WorkshopEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['workshop', 'student', 'enrolled_at']
    list_filter = ['workshop__category', 'workshop__level', 'enrolled_at', 'workshop__status']
    search_fields = ['workshop__title', 'student__full_name', 'student__email']
    readonly_fields = ['enrolled_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('workshop', 'student')