
from django.urls import path
from . import views

urlpatterns = [
    # Mentor Management URLs
    path('', views.MentorListCreateView.as_view(), name='mentor-list-create'),
    path('<int:pk>/', views.MentorDetailView.as_view(), name='mentor-detail'),
    path('bulk-approve/', views.bulk_approve_mentors, name='bulk-approve-mentors'),

    # Student endpoints
    path('student/mentors/',views. StudentMentorListView.as_view(), name='student-mentor-list'),
    path('student/mentors/<int:pk>/', views.StudentMentorDetailView.as_view(), name='student-mentor-detail'),


]





