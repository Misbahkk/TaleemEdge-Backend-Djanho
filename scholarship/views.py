from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from authentication.models import User
from django.db.models import Count, Q
from django.utils import timezone
from .models import *
from .serializers import *
from .utils import send_notification


class IsAdminUser(permissions.BasePermission):
    """Custom permission to only allow admin users."""
    
    def has_permission(self, request, view):
       
        # print(request.user.role == 'admin')
        return (request.user and request.user.is_authenticated and 
                
                getattr(request.user,'role',None) == 'admin')
    


class IsStudentUser(permissions.BasePermission):
    """Custom permission to only allow student users."""
    
    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated and 
                
               getattr(request.user,'role',None) == 'student')


# ADMIN VIEWS
class AdminScholarshipListCreateView(generics.ListCreateAPIView):
    """Admin can view all scholarships with stats and create new ones"""
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        return Scholarship.objects.all().order_by('-created_at')
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ScholarshipListSerializer
        return ScholarshipSerializer
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        # Add summary stats
        stats = {
            'total_scholarships': queryset.count(),
            'active_scholarships': queryset.filter(status='active').count(),
            'upcoming_scholarships': queryset.filter(status='upcoming').count(),
            'closed_scholarships': queryset.filter(status='closed').count(),
            'total_applications': ScholarshipApplication.objects.count(),
        }
        
        return Response({
            'scholarships': serializer.data,
            'stats': stats
        })


class AdminScholarshipDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Admin can view, update, delete specific scholarship with application details"""
    queryset = Scholarship.objects.all()
    serializer_class = ScholarshipSerializer
    permission_classes = [IsAdminUser]
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # Get applications for this scholarship
        applications = ScholarshipApplication.objects.filter(
            scholarship=instance
        ).select_related('student')
        
        applications_data = ScholarshipApplicationSerializer(
            applications, many=True
        ).data
        
        return Response({
            'scholarship': serializer.data,
            'applications': applications_data,
            'applications_count': applications.count()
        })


class AdminDashboardView(generics.GenericAPIView):
    """Admin dashboard with overall statistics"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        # Recent applications (last 10)
        recent_applications = ScholarshipApplication.objects.select_related(
            'student', 'scholarship'
        ).order_by('-applied_at')[:10]
        
        stats = {
            'total_scholarships': Scholarship.objects.count(),
            'active_scholarships': Scholarship.objects.filter(status='active').count(),
            'total_applications': ScholarshipApplication.objects.count(),
            'pending_applications': ScholarshipApplication.objects.filter(status='pending').count(),
            'recent_applications': ScholarshipApplicationSerializer(recent_applications, many=True).data
        }
        
        return Response(stats)


class AdminApplicationsListView(generics.ListAPIView):
    """Admin can view all applications"""
    serializer_class = ScholarshipApplicationSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        queryset = ScholarshipApplication.objects.select_related(
            'student', 'scholarship'
        ).order_by('-applied_at')
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by scholarship if provided
        scholarship_id = self.request.query_params.get('scholarship')
        if scholarship_id:
            queryset = queryset.filter(scholarship_id=scholarship_id)
        
        return queryset


class AdminApplicationDetailView(generics.RetrieveUpdateAPIView):
    """Admin can view and update application status"""
    queryset = ScholarshipApplication.objects.all()
    serializer_class = ScholarshipApplicationSerializer
    permission_classes = [IsAdminUser]
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_status = instance.status
        
        response = super().update(request, *args, **kwargs)
        
        # Send notification if status changed
        if instance.status != old_status:
            send_notification(
                user=instance.student,
                title=f"Scholarship Application Status Updated",
                message=f"Your application for '{instance.scholarship.title}' has been {instance.status}.",
                notification_type='scholarship_status_update',
                scholarship=instance.scholarship,
                application=instance
            )
        
        return response


# STUDENT VIEWS
class StudentScholarshipListView(generics.ListAPIView):
    """Students can view all active scholarships with their application status"""
    serializer_class = StudentDashboardSerializer
    permission_classes = [IsStudentUser]
    
    def get_queryset(self):
        return Scholarship.objects.filter(
            Q(status='active') | Q(status='upcoming')
        ).order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        
        # Get student's application stats
        user_applications = ScholarshipApplication.objects.filter(student=request.user)
        
        stats = {
            'total_available_scholarships': queryset.count(),
            'user_total_applications': user_applications.count(),
            'user_pending_applications': user_applications.filter(status='pending').count(),
            'user_approved_applications': user_applications.filter(status='approved').count(),
        }
        
        return Response({
            'scholarships': serializer.data,
            'stats': stats
        })


class StudentScholarshipDetailView(generics.RetrieveAPIView):
    """Students can view detailed scholarship information"""
    serializer_class = ScholarshipSerializer
    permission_classes = [IsStudentUser]
    
    def get_queryset(self):
        return Scholarship.objects.filter(
            Q(status='active') | Q(status='upcoming')
        )
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # Check if student has applied
        has_applied = ScholarshipApplication.objects.filter(
            scholarship=instance, student=request.user
        ).exists()
        
        application_status = None
        if has_applied:
            application = ScholarshipApplication.objects.get(
                scholarship=instance, student=request.user
            )
            application_status = application.status
        
        return Response({
            'scholarship': serializer.data,
            'has_applied': has_applied,
            'application_status': application_status,
            'can_apply': not has_applied and instance.status == 'active' and not instance.is_full
        })


class StudentApplyScholarshipView(generics.CreateAPIView):
    """Students can apply for scholarships"""
    serializer_class = ScholarshipApplicationCreateSerializer
    permission_classes = [IsStudentUser]
    
    def perform_create(self, serializer):
        application = serializer.save(student=self.request.user)
        
        # Send notification to all admins
        admin_users = User.objects.filter(role='admin')
        for admin in admin_users:
            send_notification(
                user=admin,
                title="New Scholarship Application",
                message=f"{self.request.user.get_full_name() or self.request.user.username} applied for '{application.scholarship.title}'",
                notification_type='scholarship_application',
                scholarship=application.scholarship,
                application=application
            )
        
        return application


class StudentApplicationsListView(generics.ListAPIView):
    """Students can view their own applications"""
    serializer_class = StudentApplicationsListSerializer
    permission_classes = [IsStudentUser]
    
    def get_queryset(self):
        return ScholarshipApplication.objects.filter(
            student=self.request.user
        ).select_related('scholarship').order_by('-applied_at')


# SHARED VIEWS
class NotificationListView(generics.ListAPIView):
    """Users can view their notifications"""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notification_read(request, notification_id):
    """Mark notification as read"""
    try:
        notification = Notification.objects.get(
            id=notification_id, user=request.user
        )
        notification.is_read = True
        notification.save()
        return Response({'message': 'Notification marked as read'})
    except Notification.DoesNotExist:
        return Response(
            {'error': 'Notification not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_notifications_read(request):
    """Mark all notifications as read"""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return Response({'message': 'All notifications marked as read'})


# PUBLIC VIEWS (for non-authenticated users to browse)
class PublicScholarshipListView(generics.ListAPIView):
    """Public view of active scholarships"""
    serializer_class = ScholarshipListSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return Scholarship.objects.filter(status='active').order_by('-created_at')


class PublicScholarshipDetailView(generics.RetrieveAPIView):
    """Public detailed view of scholarship"""
    serializer_class = ScholarshipSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return Scholarship.objects.filter(status='active')