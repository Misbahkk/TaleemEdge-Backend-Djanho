# workshops/views.py
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count


from .models import Workshop, WorkshopEnrollment
from .serializers import (
    WorkshopSerializer, 
    AdminWorkshopSerializer, 
    WorkshopEnrollmentSerializer
)
from authentication.models import PlatformActivity

# ================ ADMIN VIEWS ================
class AdminWorkshopListCreateView(generics.ListCreateAPIView):
    """Admin can create workshops and view their own workshops"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role != 'admin':
            return Workshop.objects.none()
        
        queryset = Workshop.objects.filter(created_by=self.request.user)
        
        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(category__icontains=search) |
                Q(instructor__icontains=search)
            )
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        # Filter by level
        level_filter = self.request.query_params.get('level', None)
        if level_filter:
            queryset = queryset.filter(level=level_filter)
        
        return queryset.annotate(enrolled_students_count=Count('enrollments'))
    
    def get_serializer_class(self):
        return AdminWorkshopSerializer
    
    def perform_create(self, serializer):
        if self.request.user.role != 'admin':
            raise Response("Only admins can create workshops",status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save(created_by=self.request.user)
        
        # Log activity
        PlatformActivity.objects.create(
            activity_type='workshop_created',
            user_name=self.request.user.full_name,
            description=f"{self.request.user.full_name} created workshop: {serializer.instance.title}"
        )

class AdminWorkshopDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Admin can view, update, and delete their workshops"""
    serializer_class = AdminWorkshopSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role != 'admin':
            return Workshop.objects.none()
        return Workshop.objects.filter(created_by=self.request.user)
    
    def perform_destroy(self, instance):
        # Log activity before deletion
        PlatformActivity.objects.create(
            activity_type='workshop_deleted',
            user_name=self.request.user.full_name,
            description=f"{self.request.user.full_name} deleted workshop: {instance.title}"
        )
        super().perform_destroy(instance)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_dashboard_stats(request):
    """Get dashboard statistics for admin"""
    if request.user.role != 'admin':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    workshops = Workshop.objects.filter(created_by=request.user)
    
    stats = {
        'total_workshops': workshops.count(),
        'upcoming_workshops': workshops.filter(status='upcoming').count(),
        'ongoing_workshops': workshops.filter(status='ongoing').count(),
        'completed_workshops': workshops.filter(status='completed').count(),
        'total_enrollments': WorkshopEnrollment.objects.filter(workshop__created_by=request.user).count(),
        'recent_workshops': AdminWorkshopSerializer(
            workshops[:5], many=True, context={'request': request}
        ).data
    }
    
    return Response(stats)

# ================ STUDENT VIEWS ================
class StudentWorkshopListView(generics.ListAPIView):
    """Students can view all workshops"""
    serializer_class = WorkshopSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = Workshop.objects.all()
        
        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(category__icontains=search) |
                Q(instructor__icontains=search)
            )
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        # Filter by level
        level_filter = self.request.query_params.get('level', None)
        if level_filter:
            queryset = queryset.filter(level=level_filter)
            
        # Filter by category
        category_filter = self.request.query_params.get('category', None)
        if category_filter:
            queryset = queryset.filter(category__icontains=category_filter)
        
        return queryset.annotate(enrolled_students_count=Count('enrollments'))

class StudentWorkshopDetailView(generics.RetrieveAPIView):
    """Student can view workshop details"""
    queryset = Workshop.objects.all()
    serializer_class = WorkshopSerializer
    permission_classes = [AllowAny]

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_enrolled_workshops(request):
    """Get workshops that student is enrolled in"""
    if request.user.role != 'student':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    # Filter parameters
    status_filter = request.query_params.get('status', None)
    search = request.query_params.get('search', None)
    
    enrollments = WorkshopEnrollment.objects.filter(student=request.user).select_related('workshop')
    
    if status_filter:
        enrollments = enrollments.filter(workshop__status=status_filter)
    
    if search:
        enrollments = enrollments.filter(
            Q(workshop__title__icontains=search) |
            Q(workshop__category__icontains=search) |
            Q(workshop__instructor__icontains=search)
        )
    
    serializer = WorkshopEnrollmentSerializer(enrollments, many=True, context={'request': request})
    return Response({
        'enrolled_workshops': serializer.data,
        'total_count': enrollments.count()
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_dashboard(request):
    """Get dashboard data for student"""
    if request.user.role != 'student':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    enrollments = WorkshopEnrollment.objects.filter(student=request.user).select_related('workshop')
    
    dashboard_data = {
        'total_enrollments': enrollments.count(),
        'upcoming_workshops': enrollments.filter(workshop__status='upcoming').count(),
        'completed_workshops': enrollments.filter(workshop__status='completed').count(),
        'recent_enrollments': WorkshopEnrollmentSerializer(
            enrollments[:5], many=True, context={'request': request}
        ).data
    }
    
    return Response(dashboard_data)

# ================ ENROLLMENT VIEWS ================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enroll_workshop(request, workshop_id):
    """Student enrolls in a workshop"""
    if request.user.role != 'student':
        return Response({'error': 'Only students can enroll in workshops'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    workshop = get_object_or_404(Workshop, id=workshop_id)
    
    # Check if workshop is full
    if workshop.enrollments.count() >= workshop.capacity:
        return Response({'error': 'Workshop is full'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if user is already enrolled
    if WorkshopEnrollment.objects.filter(workshop=workshop, student=request.user).exists():
        return Response({'error': 'Already enrolled in this workshop'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    # Check if workshop is still accepting enrollments
    if workshop.status in ['completed', 'cancelled']:
        return Response({'error': 'Cannot enroll in this workshop'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    # Create enrollment
    enrollment = WorkshopEnrollment.objects.create(
        workshop=workshop,
        student=request.user
    )
    
    # Update enrolled count (for backward compatibility)
    workshop.enrolled_count = workshop.enrollments.count()
    workshop.save()
    
    # Log activity
    PlatformActivity.objects.create(
        activity_type='workshop_enrollment',
        user_name=request.user.full_name,
        description=f"{request.user.full_name} enrolled in {workshop.title}"
    )
    
    return Response({
        'message': 'Successfully enrolled in workshop',
        'enrollment': WorkshopEnrollmentSerializer(enrollment, context={'request': request}).data
    })

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def unenroll_workshop(request, workshop_id):
    """Student unenrolls from a workshop"""
    if request.user.role != 'student':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    workshop = get_object_or_404(Workshop, id=workshop_id)
    
    try:
        enrollment = WorkshopEnrollment.objects.get(workshop=workshop, student=request.user)
        enrollment.delete()
        
        # Update enrolled count
        workshop.enrolled_count = workshop.enrollments.count()
        workshop.save()
        
        # Log activity
        PlatformActivity.objects.create(
            activity_type='workshop_unenrollment',
            user_name=request.user.full_name,
            description=f"{request.user.full_name} unenrolled from {workshop.title}"
        )
        
        return Response({'message': 'Successfully unenrolled from workshop'})
        
    except WorkshopEnrollment.DoesNotExist:
        return Response({'error': 'Not enrolled in this workshop'}, 
                       status=status.HTTP_400_BAD_REQUEST)

# ================ UTILITY VIEWS ================
@api_view(['GET'])
def workshop_categories(request):
    """Get all unique workshop categories"""
    categories = Workshop.objects.values_list('category', flat=True).distinct().order_by('category')
    print("categories: ",categories)
    return Response({'categories': list(categories)})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def workshop_enrollments_detail(request, workshop_id):
    """Admin can view detailed enrollment information for their workshop"""
    if request.user.role != 'admin':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    workshop = get_object_or_404(Workshop, id=workshop_id, created_by=request.user)
    enrollments = WorkshopEnrollment.objects.filter(workshop=workshop).select_related('student')
    
    enrollment_data = [{
        'id': enrollment.id,
        'student_name': enrollment.student.full_name,
        'student_email': enrollment.student.email,
        'enrolled_at': enrollment.enrolled_at,
        'student_id': enrollment.student.id
    } for enrollment in enrollments]
    
    return Response({
        'workshop_title': workshop.title,
        'total_enrollments': enrollments.count(),
        'capacity': workshop.capacity,
        'enrollments': enrollment_data
    })