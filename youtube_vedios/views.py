
# views.py
from rest_framework import viewsets, status
from django.db import models
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Video
from .serializers import VideoSerializer, VideoCreateSerializer, VideoUpdateSerializer
from .permissions import IsAdminOrReadOnly

class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return VideoCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return VideoUpdateSerializer
        return VideoSerializer
    
    def create(self, request, *args, **kwargs):
        """Admin can create new video"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        video = serializer.save()
        
        response_serializer = VideoSerializer(video)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """Admin can update video"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        video = serializer.save()
        
        response_serializer = VideoSerializer(video)
        return Response(response_serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """Admin can delete video"""
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    def list(self, request, *args, **kwargs):
        """All users can get all videos"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Filter by category if provided
        category = request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category__icontains=category)
        
        # Search in title and description
        search = request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                models.Q(title__icontains=search) | 
                models.Q(description__icontains=search)
            )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    def retrieve(self, request, *args, **kwargs):
        """All users can get single video by ID"""
        instance = self.get_object()
        
        try:
            # Safer view count parsing and incrementing
            current_views_str = instance.views or '0'
            
            # Extract numeric value
            if 'M' in current_views_str:
                current_views = int(float(current_views_str.replace('M', '')) * 1000000)
            elif 'K' in current_views_str:
                current_views = int(float(current_views_str.replace('K', '')) * 1000)
            else:
                current_views = int(''.join(filter(str.isdigit, current_views_str)) or '0')
            
            # Increment views
            current_views += 1
            
            # Format views back to K/M format
            if current_views >= 1000000:
                instance.views = f"{current_views // 1000000}M"
            elif current_views >= 1000:
                instance.views = f"{current_views // 1000}K"
            else:
                instance.views = str(current_views)
            
            instance.save(update_fields=['views'])
            
        except (ValueError, AttributeError) as e:
            # If view count parsing fails, just increment by 1 from current string
            print(f"View count parsing error: {e}")
            # Don't fail the request, just log and continue
            pass
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def categories(self, request):
        """Get all unique categories"""
        categories = Video.objects.values_list('category', flat=True).distinct()
        return Response({'categories': list(categories)})
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def by_category(self, request):
        """Get videos grouped by category"""
        videos_by_category = {}
        categories = Video.objects.values_list('category', flat=True).distinct()
        
        for category in categories:
            videos = Video.objects.filter(category=category)
            videos_by_category[category] = VideoSerializer(videos, many=True).data
        
        return Response(videos_by_category)

