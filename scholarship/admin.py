from django.contrib import admin
from .models import Scholarship, ScholarshipApplication, Notification



@admin.register(Scholarship)
class ScholarshipAdmin(admin.ModelAdmin):
    list_display = ['title', 'provider', 'amount', 'deadline', 'status', 'total_applications', 'max_applicants', 'created_at']
    list_filter = ['status', 'academic_level', 'category', 'country', 'created_at']
    search_fields = ['title', 'provider', 'category', 'country']
    readonly_fields = ['created_at', 'total_applications']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'provider', 'description', 'amount')
        }),
        ('Application Details', {
            'fields': ('deadline', 'category', 'max_applicants', 'academic_level', 'country', 'application_url')
        }),
        ('Requirements', {
            'fields': ('eligibility_criteria', 'requirements', 'benefits')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Statistics', {
            'fields': ('total_applications', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_applications(self, obj):
        return obj.applications.count()
    total_applications.short_description = 'Total Applications'


@admin.register(ScholarshipApplication)
class ScholarshipApplicationAdmin(admin.ModelAdmin):
    list_display = ['student', 'scholarship', 'status', 'applied_at']
    list_filter = ['status', 'applied_at', 'scholarship__category']
    search_fields = ['student__username', 'student__email', 'scholarship__title']
    readonly_fields = ['applied_at']
    
    fieldsets = (
        ('Application Info', {
            'fields': ('scholarship', 'student', 'applied_at')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Notes', {
            'fields': ('notes', 'admin_notes')
        }),
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    readonly_fields = ['created_at']