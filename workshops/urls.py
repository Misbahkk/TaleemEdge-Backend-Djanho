# workshops/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # ================ ADMIN URLs ================
    # Admin workshop management
    path('admin/', views.AdminWorkshopListCreateView.as_view(), name='admin-workshop-list-create'),
    path('admin/<int:pk>/', views.AdminWorkshopDetailView.as_view(), name='admin-workshop-detail'),
    path('admin/dashboard/stats/', views.admin_dashboard_stats, name='admin-dashboard-stats'),
    path('admin/<int:workshop_id>/enrollments/', views.workshop_enrollments_detail, name='workshop-enrollments-detail'),
    
    # ================ STUDENT URLs ================
    # Student workshop views
    path('student/', views.StudentWorkshopListView.as_view(), name='student-workshop-list'),
    path('student/<int:pk>/', views.StudentWorkshopDetailView.as_view(), name='student-workshop-detail'),
    path('student/enrolled-workshops/', views.student_enrolled_workshops, name='student-enrolled-workshops'),
    path('student/dashboard/', views.student_dashboard, name='student-dashboard'),
    
    # ================ ENROLLMENT URLs ================
    # Workshop enrollment/unenrollment
    path('student/<int:workshop_id>/enroll/', views.enroll_workshop, name='workshop-enroll'),
    path('student/<int:workshop_id>/unenroll/', views.unenroll_workshop, name='workshop-unenroll'),
    
    # ================ UTILITY URLs ================
    # Utility endpoints
    path('categories/', views.workshop_categories, name='workshop-categories'),
]