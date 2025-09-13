from django.urls import path
from . import views

urlpatterns = [
    # PUBLIC URLS (No authentication required)
    path('public/', views.PublicScholarshipListView.as_view(), name='public-scholarship-list'),
    path('public/<int:pk>/', views.PublicScholarshipDetailView.as_view(), name='public-scholarship-detail'),
    
    # ADMIN URLS
    path('admin/dashboard/', views.AdminDashboardView.as_view(), name='admin-dashboard'),
    path('admin/', views.AdminScholarshipListCreateView.as_view(), name='admin-scholarship-list-create'),
    path('admin/<int:pk>/', views.AdminScholarshipDetailView.as_view(), name='admin-scholarship-detail'),
    path('admin/applications/', views.AdminApplicationsListView.as_view(), name='admin-applications-list'),
    path('admin/applications/<int:pk>/', views.AdminApplicationDetailView.as_view(), name='admin-application-detail'),
    
    # STUDENT URLS
    path('student/', views.StudentScholarshipListView.as_view(), name='student-scholarship-list'),
    path('student/<int:pk>/', views.StudentScholarshipDetailView.as_view(), name='student-scholarship-detail'),
    path('student/apply/', views.StudentApplyScholarshipView.as_view(), name='student-apply-scholarship'),
    path('student/applications/', views.StudentApplicationsListView.as_view(), name='student-applications-list'),
    
    # NOTIFICATIONS (Both Admin & Student)
    path('notifications/', views.NotificationListView.as_view(), name='notification-list'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark-notification-read'),
    path('notifications/read-all/', views.mark_all_notifications_read, name='mark-all-notifications-read'),
]