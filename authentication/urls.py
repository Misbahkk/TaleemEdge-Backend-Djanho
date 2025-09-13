
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.UserRegistrationView.as_view(), name='user-register'),
    path('login/', views.UserLoginView.as_view(), name='user-login'),
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),

    # Admin Dashboard URLs
    path('admin/dashboard/stats/', views.DashboardStatsView.as_view(), name='dashboard-stats'),
    path('admin/dashboard/activities/', views.PlatformActivityView.as_view(), name='platform-activities'),
    path('admin/dashboard/tasks/', views.PendingTasksView.as_view(), name='pending-tasks'),
    path('admin/analytics/', views.AnalyticsView.as_view(), name='analytics'),
    path('admin/monthly-stats/', views.monthly_stats, name='monthly-stats'),

    
    # Platform Settings URLs
    path('admin/settings/', views.PlatformSettingsView.as_view(), name='platform-settings'),
    path('settings/public/', views.PublicSettingsView.as_view(), name='public-settings'),
    
    # User Management URLs
    path('admin/users/', views.UserListView.as_view(), name='user-list'),
    # path('admin/users/<int:user_id>/toggle-status/', views.toggle_user_status, name='toggle-user-status'),
    


]

# Authentication URLs
