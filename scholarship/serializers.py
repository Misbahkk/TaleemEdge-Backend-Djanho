from rest_framework import serializers
from authentication.models import User
from .models import *
from authentication.serializers import UserSerializer

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['id', 'username', 'email', 'first_name', 'last_name']


class ScholarshipSerializer(serializers.ModelSerializer):
    eligibility_criteria_list = serializers.SerializerMethodField()
    requirements_list = serializers.SerializerMethodField()
    benefits_list = serializers.SerializerMethodField()
    total_applications = serializers.ReadOnlyField()
    is_full = serializers.ReadOnlyField()
    
    class Meta:
        model = Scholarship
        fields = '__all__'
    
    def get_eligibility_criteria_list(self, obj):
        return [criteria.strip() for criteria in obj.eligibility_criteria.split(',') if criteria.strip()]
    
    def get_requirements_list(self, obj):
        return [req.strip() for req in obj.requirements.split(',') if req.strip()]
    
    def get_benefits_list(self, obj):
        return [benefit.strip() for benefit in obj.benefits.split(',') if benefit.strip()]


class ScholarshipListSerializer(serializers.ModelSerializer):
    """Lighter serializer for list views"""
    total_applications = serializers.ReadOnlyField()
    is_full = serializers.ReadOnlyField()
    
    class Meta:
        model = Scholarship
        fields = ['id', 'title', 'provider', 'amount', 'deadline', 'category', 
                 'academic_level', 'country', 'status', 'total_applications', 
                 'is_full', 'max_applicants', 'created_at']


class ScholarshipApplicationSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    scholarship = ScholarshipListSerializer(read_only=True)
    
    class Meta:
        model = ScholarshipApplication
        fields = '__all__'


class ScholarshipApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScholarshipApplication
        fields = ['scholarship', 'notes']
    
    def validate_scholarship(self, value):
        user = self.context['request'].user
        
        # Check if user already applied
        if ScholarshipApplication.objects.filter(scholarship=value, student=user).exists():
            raise serializers.ValidationError("You have already applied for this scholarship.")
        
        # Check if scholarship is active
        if value.status != 'active':
            raise serializers.ValidationError("This scholarship is not currently accepting applications.")
        
        # Check if scholarship is full
        if value.is_full:
            raise serializers.ValidationError("This scholarship has reached its maximum number of applicants.")
        
        return value


class StudentDashboardSerializer(serializers.ModelSerializer):
    """Serializer to show student's application status on scholarships"""
    has_applied = serializers.SerializerMethodField()
    application_status = serializers.SerializerMethodField()
    total_applications = serializers.ReadOnlyField()
    is_full = serializers.ReadOnlyField()
    
    class Meta:
        model = Scholarship
        fields = ['id', 'title','description', 'provider', 'amount', 'deadline', 'category',
                 'academic_level', 'country', 'status', 'has_applied', 
                 'application_status','application_url', 'total_applications', 'is_full',
                 'max_applicants']
    
    def get_has_applied(self, obj):
        user = self.context['request'].user
        return ScholarshipApplication.objects.filter(
            scholarship=obj, student=user
        ).exists()
    
    def get_application_status(self, obj):
        user = self.context['request'].user
        application = ScholarshipApplication.objects.filter(
            scholarship=obj, student=user
        ).first()
        return application.status if application else None


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['user', 'created_at']


class AdminDashboardStatsSerializer(serializers.Serializer):
    total_scholarships = serializers.IntegerField()
    active_scholarships = serializers.IntegerField()
    total_applications = serializers.IntegerField()
    pending_applications = serializers.IntegerField()
    recent_applications = ScholarshipApplicationSerializer(many=True)


class StudentApplicationsListSerializer(serializers.ModelSerializer):
    scholarship = ScholarshipListSerializer(read_only=True)
    
    class Meta:
        model = ScholarshipApplication
        fields = ['id', 'scholarship', 'applied_at', 'status', 'notes', 'admin_notes']