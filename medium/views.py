# views.py
from rest_framework import generics, status, filters
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import BlogPost, Category
from .serializers import (
    BlogPostSerializer, BlogPostCreateSerializer, 
    BlogPostListSerializer, CategorySerializer
)
from .permissions import is_admin_user,is_student_user

class BlogPostListView(generics.ListAPIView):
    """Get all blog posts with filtering and search"""
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'author']
    search_fields = ['title', 'author', 'tags', 'excerpt']
    ordering_fields = ['created_at', 'views', 'title']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by tags
        tags = self.request.query_params.get('tags', None)
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
            for tag in tag_list:
                queryset = queryset.filter(tags__icontains=tag)
        
        return queryset

class BlogPostDetailView(generics.RetrieveAPIView):
    """Get single blog post by ID"""
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment views
        instance.views += 1
        instance.save(update_fields=['views'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class BlogPostCreateView(generics.CreateAPIView):
    """Create new blog post"""
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostCreateSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            blog_post = serializer.save()
            return_serializer = BlogPostSerializer(blog_post)
            return Response(return_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BlogPostUpdateView(generics.UpdateAPIView):
    """Update existing blog post"""
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BlogPostDeleteView(generics.DestroyAPIView):
    """Delete blog post"""
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer

# Category Views
class CategoryListView(generics.ListCreateAPIView):
    """List all categories or create new category"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update or delete category"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

# Custom API Views
@api_view(['GET'])
@permission_classes([AllowAny])
def blog_stats(request):
    """Get blog statistics"""
    user = request.user
    
    if is_admin_user(user):
        # Admin can see all stats
        total_posts = BlogPost.objects.count()
        published_posts = BlogPost.objects.filter(status='published').count()
        draft_posts = BlogPost.objects.filter(status='draft').count()
        total_views = sum(BlogPost.objects.values_list('views', flat=True))
    else:
        # Students and public can only see published stats
        published_posts = BlogPost.objects.filter(status='published').count()
        total_views = sum(BlogPost.objects.filter(status='published').values_list('views', flat=True))
        total_posts = published_posts
        draft_posts = 0
    
    return Response({
        'total_posts': total_posts,
        'published_posts': published_posts,
        'draft_posts': draft_posts,
        'total_views': total_views
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def featured_posts(request):
    """Get featured posts (most viewed published posts)"""
    posts = BlogPost.objects.filter(status='published').order_by('-views')[:3]
    serializer = BlogPostListSerializer(posts, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def posts_by_tag(request, tag_name):
    """Get published posts by specific tag"""
    posts = BlogPost.objects.filter(
        tags__icontains=tag_name,
        status='published'
    ).order_by('-created_at')
    serializer = BlogPostListSerializer(posts, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
def increment_views(request, pk):
    """Increment view count for a post"""
    try:
        user = request.user
        
        if is_admin_user(user):
            post = BlogPost.objects.get(pk=pk)
        else:
            # Students and public can only access published posts
            post = BlogPost.objects.get(pk=pk, status='published')
            
        post.views += 1
        post.save(update_fields=['views'])
        return Response({'message': 'Views incremented', 'views': post.views})
    except BlogPost.DoesNotExist:
        return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

# User role checking endpoints
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_role(request):
    """Get current user's role"""
    user = request.user
    
    role = 'student'  # default
    if is_admin_user(user):
        role = 'admin'
    
    return Response({
        'user_id': user.id,
        'username': user.username,
        'role': role,
        'is_admin': is_admin_user(user),
        'is_student': is_student_user(user)
    })