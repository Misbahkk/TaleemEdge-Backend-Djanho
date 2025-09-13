# workshops/serializers.py
from rest_framework import serializers
from .models import Workshop, WorkshopEnrollment
from django.contrib.auth import get_user_model

User = get_user_model()

class WorkshopSerializer(serializers.ModelSerializer):
    enrolled_students_count = serializers.SerializerMethodField()
    is_enrolled = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    main_image_url = serializers.SerializerMethodField()
    video_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Workshop
        fields = '__all__'
        read_only_fields = ('created_by', 'enrolled_count', 'created_at', 'updated_at')
    
    def get_enrolled_students_count(self, obj):
        return obj.enrollments.count()
    
    def get_is_enrolled(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user.role == 'student':
            return obj.enrollments.filter(student=request.user).exists()
        return False
    
    def get_main_image_url(self, obj):
        if obj.main_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.main_image.url)
        return None
    
    def get_video_url(self, obj):
        if obj.video:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.video.url)
        return None

class AdminWorkshopSerializer(serializers.ModelSerializer):
    """Serializer for admin with additional details"""
    enrolled_students_count = serializers.SerializerMethodField()
    enrolled_students = serializers.SerializerMethodField()
    main_image_url = serializers.SerializerMethodField()
    video_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Workshop
        fields = '__all__'
        read_only_fields = ('created_by', 'enrolled_count', 'created_at', 'updated_at')
    
    def get_enrolled_students_count(self, obj):
        return obj.enrollments.count()
    
    def get_enrolled_students(self, obj):
        enrollments = obj.enrollments.select_related('student')[:10]  # Limit to 10 for performance
        return [{
            'id': enrollment.student.id,
            'name': enrollment.student.full_name,
            'email': enrollment.student.email,
            'enrolled_at': enrollment.enrolled_at
        } for enrollment in enrollments]
    
    def get_main_image_url(self, obj):
        if obj.main_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.main_image.url)
        return None
    
    def get_video_url(self, obj):
        if obj.video:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.video.url)
        return None

class WorkshopEnrollmentSerializer(serializers.ModelSerializer):
    workshop_title = serializers.CharField(source='workshop.title', read_only=True)
    workshop_date = serializers.DateField(source='workshop.date', read_only=True)
    workshop_time = serializers.TimeField(source='workshop.time', read_only=True)
    workshop_instructor = serializers.CharField(source='workshop.instructor', read_only=True)
    workshop_status = serializers.CharField(source='workshop.status', read_only=True)
    workshop = WorkshopSerializer(read_only=True)
    
    class Meta:
        model = WorkshopEnrollment
        fields = ['id', 'workshop', 'workshop_title', 'workshop_date', 'workshop_time', 
                 'workshop_instructor', 'workshop_status', 'enrolled_at']

class StudentDashboardSerializer(serializers.Serializer):
    """Serializer for student dashboard data"""
    total_enrollments = serializers.IntegerField()
    upcoming_workshops = serializers.IntegerField()
    completed_workshops = serializers.IntegerField()
    recent_enrollments = WorkshopEnrollmentSerializer(many=True)