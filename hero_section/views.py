# views.py
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes,authentication_classes
from rest_framework.permissions import AllowAny
from django.http import JsonResponse
from .models import HeroSection, FeatureCard
from .serializers import HeroSectionSerializer, FeatureCardSerializer

@api_view(['GET'])
@permission_classes([AllowAny]) 
@authentication_classes([])  
def hero_section_api(request):
    """API endpoint to get hero section data"""
    try:
        hero = HeroSection.objects.filter(is_active=True).first()
        if not hero:
            return JsonResponse({'error': 'No active hero section found'}, status=404)
        
        data = {
            'title': hero.title,
            'subtitle': hero.subtitle,
            'heading': hero.heading,
            'description': hero.description,
            'hero_video': hero.hero_video.url if hero.hero_video else None,
            'hero_image': hero.hero_image.url if hero.hero_image else None,
            'video_poster': hero.video_poster.url if hero.video_poster else None,
            'stats': {
                'rating': float(hero.rating),
                'students': hero.total_students,
                'resources': hero.total_resources
            },
            'buttons': {
                'primary': {
                    'text': hero.primary_button_text,
                    'link': hero.primary_button_link
                },
                'secondary': {
                    'text': hero.secondary_button_text,
                    'link': hero.secondary_button_link
                }
            }
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def feature_cards_api(request):
    """API endpoint to get feature cards"""
    try:
        features = FeatureCard.objects.filter(is_active=True).order_by('order')
        data = []
        
        for feature in features:
            data.append({
                'id': feature.id,
                'title': feature.title,
                'description': feature.description,
                'icon': feature.icon,
                'color': feature.color,
                'order': feature.order
            })
        
        return JsonResponse({'features': data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
