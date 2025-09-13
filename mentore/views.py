# views.py
from rest_framework import generics, status, permissions, filters
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import *
from .serializers import *
from authentication.models import PlatformActivity


class MentorListCreateView(generics.ListCreateAPIView):
    queryset = Mentor.objects.all()
    serializer_class = MentorSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        if response.status_code == 201:
            mentor = Mentor.objects.get(id=response.data['id'])
            PlatformActivity.objects.create(
                activity_type='mentor_application',
                user_name=mentor.full_name,
                description=f"New mentor application from {mentor.full_name}"
            )
        return response

class MentorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Mentor.objects.all()
    serializer_class = MentorSerializer
    permission_classes = [IsAuthenticated]



# Bulk Operations Views
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_approve_mentors(request):
    if request.user.role != 'admin':
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    mentor_ids = request.data.get('mentor_ids', [])
    action = request.data.get('action', 'approve')  # approve, reject
    
    if not mentor_ids:
        return Response({'error': 'mentor_ids required'}, status=status.HTTP_400_BAD_REQUEST)
    
    updated_count = Mentor.objects.filter(
        id__in=mentor_ids
    ).update(status='approved' if action == 'approve' else 'rejected')
    
    return Response({
        'message': f'Successfully {action}d {updated_count} mentors',
        'updated_count': updated_count
    })


# ✅ Students: Get all approved mentors (with search)
class StudentMentorListView(generics.ListAPIView):
    serializer_class = MentorSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['full_name', 'job_title', 'company', 'expertise_areas', 'specializations', 'languages']

    def get_queryset(self):
        return Mentor.objects.filter(status='approved')
    

# ✅ Students: Get mentor by ID (only if approved)
class StudentMentorDetailView(generics.RetrieveAPIView):
    serializer_class = MentorSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Mentor.objects.filter(status='approved')