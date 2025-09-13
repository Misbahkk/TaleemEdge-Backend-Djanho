
# serializers.py (create this file)
from rest_framework import serializers
from .models import HeroSection, FeatureCard

class HeroSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeroSection
        fields = '__all__'

class FeatureCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeatureCard
        fields = '__all__'