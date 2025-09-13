# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'blog'

urlpatterns = [
    # Public Blog Post URLs (Students & Public can access)
    path('posts/', views.BlogPostListView.as_view(), name='post-list'),
    path('posts/<int:pk>/', views.BlogPostDetailView.as_view(), name='post-detail'),
    path('posts/<int:pk>/increment-views/', views.increment_views, name='post-increment-views'),
    
    # Admin Only URLs
    path('admin/posts/', views.BlogPostListView.as_view(), name='admin-post-list'),
    path('admin/posts/create/', views.BlogPostCreateView.as_view(), name='post-create'),
    path('admin/posts/<int:pk>/update/', views.BlogPostUpdateView.as_view(), name='post-update'),
    path('admin/posts/<int:pk>/delete/', views.BlogPostDeleteView.as_view(), name='post-delete'),
    
    # Category URLs
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/<int:pk>/', views.CategoryDetailView.as_view(), name='category-detail'),
    
    # Public endpoints
    path('stats/', views.blog_stats, name='blog-stats'),
    path('featured/', views.featured_posts, name='featured-posts'),
    path('tags/<str:tag_name>/', views.posts_by_tag, name='posts-by-tag'),
    
    # User role endpoint
    path('user/role/', views.user_role, name='user-role'),
]
