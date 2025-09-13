# serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import *

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['full_name', 'email', 'password', 'confirm_password', 'school_name', 'role']
        extra_kwargs = {
            'role': {'default': 'student'}
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            full_name=validated_data['full_name'],
            school_name=validated_data.get('school_name', ''),
            role=validated_data.get('role', 'student')
        )
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        print(f"Login attempt - Email: {email}, Password: {password}")  # Debug line
        
        if email and password:
            user = authenticate(username=email, password=password)
            print(f"Authentication result: {user}")
            # user_obj = User.objects.get(email=email)
            # print(f"User found: {user_obj.email}, Active: {user_obj.is_active}")  # Debug line
            if not user:
                raise serializers.ValidationError('Invalid email or password.')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include email and password.')

class UserSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'full_name','profile_picture', 'email', 'role', 'school_name', 'is_verified', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_profile_picture(self,obj):
        request = self.context.get('request')
        if request and obj.profile_picture:
           return request.build_absolute_uri(obj.profile_pic.url)
        return None

class PlatformActivitySerializer(serializers.ModelSerializer):
    time_ago = serializers.SerializerMethodField()
    
    class Meta:
        model = PlatformActivity
        fields = ['id', 'activity_type', 'user_name', 'description', 'created_at', 'time_ago']
    
    def get_time_ago(self, obj):
        from django.utils import timezone
        diff = timezone.now() - obj.created_at
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"
        
class DashboardStatsSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    youtube_videos = serializers.IntegerField()
    library_books = serializers.IntegerField()
    workshops = serializers.IntegerField()
    scholarships = serializers.IntegerField()
    active_mentors = serializers.IntegerField()
    
    # Growth percentages
    users_growth = serializers.CharField()
    videos_growth = serializers.CharField()
    books_growth = serializers.CharField()
    workshops_growth = serializers.CharField()
    scholarships_growth = serializers.CharField()
    mentors_growth = serializers.CharField()


class PlatformSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlatformSettings
        fields = '__all__'