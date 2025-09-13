from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from mentore.models import Mentor
from scholarship.models import Scholarship
from library.models import  Book
from workshops.models import Workshop
from .models import *
from .serializers import *
from django.utils import timezone
from datetime import datetime, timedelta
from library.serializers import  BookSerializer
import calendar
from youtube_vedios.models import Video



class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Create activity log
        PlatformActivity.objects.create(
            activity_type='user_registration',
            user_name=user.full_name,
            description=f"New user registered with email {user.email}"
        )
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'User registered successfully',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)

class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Login successful',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class PlatformActivityView(generics.ListAPIView):
    serializer_class = PlatformActivitySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role != 'admin':
            return PlatformActivity.objects.none()
        return PlatformActivity.objects.all()[:10]  
    


# Admin Dashboard Views
class DashboardStatsView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Check if user is admin
        if request.user.role != 'admin':
            return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
        
        # Current month stats
        current_month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
        
        # Get current stats
        total_users = User.objects.count()
        youtube_videos = Video.objects.count()
        library_books = Book.objects.count()
        workshops = Workshop.objects.count()
        scholarships = Scholarship.objects.count()
        active_mentors = Mentor.objects.filter(status='approved').count()
        
        # Get last month stats for growth calculation
        def get_growth(current, last_month_start, current_month_start, model):
            last_month_count = model.objects.filter(
                created_at__lt=current_month_start
            ).count()
            if last_month_count == 0:
                return "+100%"
            growth = ((current - last_month_count) / last_month_count) * 100
            return f"{'+' if growth >= 0 else ''}{growth:.0f}%"
        
        stats = {
            'total_users': total_users,
            'youtube_videos': youtube_videos,
            'library_books': library_books,
            'workshops': workshops,
            'scholarships': scholarships,
            'active_mentors': active_mentors,
            'users_growth': get_growth(total_users, last_month_start, current_month_start, User),
            'videos_growth': get_growth(youtube_videos, last_month_start, current_month_start, Video),
            'books_growth': get_growth(library_books, last_month_start, current_month_start, Book),
            'workshops_growth': get_growth(workshops, last_month_start, current_month_start, Workshop),
            'scholarships_growth': get_growth(scholarships, last_month_start, current_month_start, Scholarship),
            'mentors_growth': get_growth(active_mentors, last_month_start, current_month_start, Mentor),
        }
        # print('videos_growth: ',get_growth(youtube_videos, last_month_start, current_month_start, Video))
        return Response(DashboardStatsSerializer(stats).data)

class PlatformActivityView(generics.ListAPIView):
    serializer_class = PlatformActivitySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role != 'admin':
            return PlatformActivity.objects.none()
        return PlatformActivity.objects.all()[:10]  # Latest 10 activities

class PendingTasksView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if request.user.role != 'admin':
            return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
        
        pending_scholarships = Scholarship.objects.filter(
            status='upcoming',
            deadline__gte=timezone.now()
        ).count()
        
        pending_mentors = Mentor.objects.filter(status='pending').count()
        
        pending_workshops = Workshop.objects.filter(
            status='upcoming',
            date__gte=timezone.now().date()
        ).count()
        
        tasks = [
            {
                'id': 1,
                'title': 'Review scholarship applications',
                'count': pending_scholarships,
                'priority': 'High Priority',
                'priority_color': 'red',
                'action': 'Review'
            },
            {
                'id': 2,
                'title': 'Approve new mentor profiles',
                'count': pending_mentors,
                'priority': 'Medium Priority',
                'priority_color': 'yellow',
                'action': 'Review'
            },
            {
                'id': 3,
                'title': 'Update workshop schedules',
                'count': pending_workshops,
                'priority': 'Low Priority',
                'priority_color': 'green',
                'action': 'Review'
            }
        ]
        
        return Response(tasks)
    

# Platform Settings Views
class PlatformSettingsView(generics.RetrieveUpdateAPIView):
    serializer_class = PlatformSettingsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        if self.request.user.role != 'admin':
            return None
        return PlatformSettings.get_settings()
    
    def get(self, request, *args, **kwargs):
        if request.user.role != 'admin':
            return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
        return super().get(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        if request.user.role != 'admin':
            return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

# Public Settings View (for frontend to get basic settings)
class PublicSettingsView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        settings = PlatformSettings.get_settings()
        data = {
            'site_name': settings.site_name,
            'site_description': settings.site_description,
            'primary_color': settings.primary_color,
            'secondary_color': settings.secondary_color,
            'logo': settings.logo.url if settings.logo else None,
            'favicon': settings.favicon.url if settings.favicon else None,
            'maintenance_mode': settings.maintenance_mode,
            'allow_new_registrations': settings.allow_new_registrations,
            'hero_title': settings.hero_title,
            'hero_subtitle': settings.hero_subtitle,
            'hero_image': settings.hero_image.url if settings.hero_image else None,
            'announcement_enabled': settings.announcement_enabled,
            'announcement_text': settings.announcement_text,
            'announcement_link': settings.announcement_link,
            'announcement_type': settings.announcement_type,
            'contact_email': settings.contact_email,
            'contact_phone': settings.contact_phone,
            'contact_address': settings.contact_address,
            'facebook_url': settings.facebook_url,
            'twitter_url': settings.twitter_url,
            'linkedin_url': settings.linkedin_url,
            'instagram_url': settings.instagram_url,
            'youtube_url': settings.youtube_url,
        }
        return Response(data)
    


# Analytics Views
class AnalyticsView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if request.user.role != 'admin':
            return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
        
        # Get date range from query params
        days = int(request.GET.get('days', 30))
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # User registrations over time
        user_registrations = []
        for i in range(days):
            date = start_date + timedelta(days=i)
            count = User.objects.filter(
                created_at__date=date.date()
            ).count()
            user_registrations.append({
                'date': date.strftime('%Y-%m-%d'),
                'count': count
            })
        
        # Most popular content
        popular_books = Book.objects.order_by('-download_count')[:5]
        # popular_videos = Video.objects.order_by('-views')[:5]
        
        # Workshop enrollments
        workshop_stats = Workshop.objects.values('title', 'enrolled_count').order_by('-enrolled_count')[:5]
        
        analytics_data = {
            'user_registrations': user_registrations,
            'popular_books': BookSerializer(popular_books, many=True).data,
            # 'popular_videos': VideoSerializer(popular_videos, many=True).data,
            'workshop_stats': list(workshop_stats),
            'total_users': User.objects.count(),
            'active_users_today': User.objects.filter(
                last_login__date=timezone.now().date()
            ).count(),
            'content_breakdown': {
                'books': Book.objects.count(),
                # 'videos': Video.objects.count(),
                'workshops': Workshop.objects.count(),
                'scholarships': Scholarship.objects.count(),
            }
        }
        
        return Response(analytics_data)


# Statistics for specific periods
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def monthly_stats(request):
    if request.user.role != 'admin':
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    year = int(request.GET.get('year', timezone.now().year))
    
    monthly_data = []
    for month in range(1, 13):
        month_start = datetime(year, month, 1)
        month_end = datetime(year, month, calendar.monthrange(year, month)[1], 23, 59, 59)
        
        users_count = User.objects.filter(
            created_at__range=[month_start, month_end]
        ).count()
        
        books_count = Book.objects.filter(
            created_at__range=[month_start, month_end]
        ).count()
        
        # videos_count = Video.objects.filter(
        #     created_at__range=[month_start, month_end]
        # ).count()
        
        workshops_count = Workshop.objects.filter(
            created_at__range=[month_start, month_end]
        ).count()
        
        monthly_data.append({
            'month': calendar.month_name[month],
            'month_num': month,
            'users': users_count,
            'books': books_count,
            # 'videos': videos_count,
            'workshops': workshops_count,
        })
    
    return Response(monthly_data)


# User Management
class UserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role != 'admin':
            return User.objects.none()
        
        role = self.request.GET.get('role')
        queryset = User.objects.all().order_by('-created_at')
        
        if role:
            queryset = queryset.filter(role=role)
        
        return queryset