# library/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Admin Book Management URLs
    path('books/', views.BookListCreateView.as_view(), name='book-list-create'),
    path('books/<int:pk>/', views.BookDetailView.as_view(), name='book-detail'),
    
    # Student Book Access URLs
    path('books/<int:pk>/read/', views.BookReadView.as_view(), name='book-read'),
    path('books/<int:pk>/download/', views.BookDownloadView.as_view(), name='book-download'),
    path('books/<int:pk>/progress/', views.UpdateReadingProgressView.as_view(), name='update-reading-progress'),
    
    # Student Dashboard and Activities
    path('student/library/', views.StudentDashboardView.as_view(), name='student-library'),
    path('student/activities/', views.StudentActivityListView.as_view(), name='student-activities'),
    path('student/reading-progress/', views.StudentReadingProgressListView.as_view(), name='student-reading-progress'),
    
    # Utility URLs
    path('categories/', views.BookCategoriesView.as_view(), name='book-categories'),
]