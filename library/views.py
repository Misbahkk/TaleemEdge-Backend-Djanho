# library/views.py
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from django.db.models import Count, Q
from django.utils import timezone
from django.http import HttpResponse, Http404
from datetime import datetime, timedelta
from .models import *
from .serializers import *
import calendar
from authentication.models import PlatformActivity

class BookListCreateView(generics.ListCreateAPIView):
    serializer_class = BookSerializer
    
    def get_queryset(self):
        queryset = Book.objects.filter(status='available')
        
        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(author__icontains=search) |
                Q(description__icontains=search)
            )
        
        # Category filter
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)
        
        # Language filter
        language = self.request.query_params.get('language', None)
        if language:
            queryset = queryset.filter(language__icontains=language)
        
        return queryset
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [AllowAny()]
    
    def create(self, request, *args, **kwargs):
        if not hasattr(request.user, 'role') or request.user.role != 'admin':
            return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)

class BookDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated()]
        return [AllowAny()]
    
    def update(self, request, *args, **kwargs):
        if not hasattr(request.user, 'role') or request.user.role != 'admin':
            return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        if not hasattr(request.user, 'role') or request.user.role != 'admin':
            return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

class BookReadView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        try:
            book = Book.objects.get(pk=pk, status='available')
        except Book.DoesNotExist:
            return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if not book.pdf_file:
            return Response({'error': 'PDF file not available'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Record read activity
        activity, created = StudentBookActivity.objects.get_or_create(
            user=request.user,
            book=book,
            activity_type='read'
        )
        
        # Update book read count
        book.read_count += 1
        book.save()
        
        # Create or update reading progress
        reading_progress, created = ReadingProgress.objects.get_or_create(
            user=request.user,
            book=book,
            defaults={'progress_percentage': 0.0, 'last_page_read': 0}
        )
        
        return Response({
            'message': 'Book opened for reading',
            'pdf_url': request.build_absolute_uri(book.pdf_file.url),
            'book_details': BookSerializer(book, context={'request': request}).data
        })

class BookDownloadView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        try:
            book = Book.objects.get(pk=pk, status='available')
        except Book.DoesNotExist:
            return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if not book.pdf_file:
            return Response({'error': 'PDF file not available'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Record download activity
        activity, created = StudentBookActivity.objects.get_or_create(
            user=request.user,
            book=book,
            activity_type='download'
        )
         # Create activity log
        PlatformActivity.objects.create(
            activity_type='book_download',
            user_name=request.user.full_name,
            description=f"New user book download with email {request.user.email}"
        )
        
        # Update book download count
        book.download_count += 1
        book.save()
        
        # Return file for download
        response = HttpResponse(book.pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{book.title}.pdf"'
        return response

class UpdateReadingProgressView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        try:
            book = Book.objects.get(pk=pk, status='available')
        except Book.DoesNotExist:
            return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
        
        progress_percentage = request.data.get('progress_percentage', 0)
        last_page_read = request.data.get('last_page_read', 0)
        
        reading_progress, created = ReadingProgress.objects.get_or_create(
            user=request.user,
            book=book,
            defaults={
                'progress_percentage': progress_percentage,
                'last_page_read': last_page_read
            }
        )
        
        if not created:
            reading_progress.progress_percentage = progress_percentage
            reading_progress.last_page_read = last_page_read
            reading_progress.is_completed = progress_percentage >= 100
            reading_progress.save()
        
        return Response({
            'message': 'Reading progress updated successfully',
            'progress': ReadingProgressSerializer(reading_progress).data
        })

class StudentDashboardView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Get student statistics
        total_books_read = StudentBookActivity.objects.filter(
            user=request.user, 
            activity_type='read'
        ).count()
        
        total_books_downloaded = StudentBookActivity.objects.filter(
            user=request.user, 
            activity_type='download'
        ).count()
        
        currently_reading = ReadingProgress.objects.filter(
            user=request.user,
            is_completed=False
        ).count()
        
        completed_books = ReadingProgress.objects.filter(
            user=request.user,
            is_completed=True
        ).count()
        
        # Recent activities (last 10)
        recent_activities = StudentBookActivity.objects.filter(
            user=request.user
        )[:10]
        
        # Current reading progress
        reading_progress = ReadingProgress.objects.filter(
            user=request.user
        )[:5]
        
        dashboard_data = {
            'total_books_read': total_books_read,
            'total_books_downloaded': total_books_downloaded,
            'currently_reading': currently_reading,
            'completed_books': completed_books,
            'recent_activities': recent_activities,
            'reading_progress': reading_progress
        }
        
        serializer = StudentDashboardSerializer(dashboard_data)
        return Response(serializer.data)

class BookCategoriesView(APIView):
    def get(self, request):
        categories = Book.CATEGORY_CHOICES
        category_counts = []
        
        for value, label in categories:
            count = Book.objects.filter(category=value, status='available').count()
            if count > 0:
                category_counts.append({
                    'value': value,
                    'label': label,
                    'count': count
                })
        
        return Response(category_counts)

class StudentActivityListView(generics.ListAPIView):
    serializer_class = StudentBookActivitySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return StudentBookActivity.objects.filter(user=self.request.user)

class StudentReadingProgressListView(generics.ListAPIView):
    serializer_class = ReadingProgressSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ReadingProgress.objects.filter(user=self.request.user)
