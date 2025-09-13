# serializers.py
from rest_framework import serializers
from .models import *


class MentorSerializer(serializers.ModelSerializer):
    expertise_areas_list = serializers.SerializerMethodField()
    specializations_list = serializers.SerializerMethodField()
    languages_list = serializers.SerializerMethodField()
    profile_picture_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Mentor
        fields = '__all__'
    
    def get_expertise_areas_list(self, obj):
        return [area.strip() for area in obj.expertise_areas.split(',') if area.strip()]
    
    def get_specializations_list(self, obj):
        return [spec.strip() for spec in obj.specializations.split(',') if spec.strip()]
    
    def get_languages_list(self, obj):
        return [lang.strip() for lang in obj.languages.split(',') if lang.strip()]
    
    def get_profile_picture_url(self, obj):
        if obj.profile_picture:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.profile_picture.url) if request else obj.profile_picture.url
        return None
