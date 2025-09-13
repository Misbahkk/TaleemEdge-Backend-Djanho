# permissions.py
from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission:
    - Admin users can perform all operations (CRUD)
    - Student users can only read (GET requests)
    - Unauthenticated users can only read published posts
    """
    
    def has_permission(self, request, view):
        # Read permissions for any request (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Write permissions only for admin users
        if request.user.is_authenticated:
            # Check if user is admin (either superuser or staff)
            return request.user.is_staff or request.user.is_superuser
        
        return False

class IsAdminUser(permissions.BasePermission):
    """
    Admin only permission for sensitive operations
    """
    def has_permission(self, request, view):
        return (request.user.is_authenticated and 
                (request.user.is_staff or request.user.is_superuser))

class StudentCanOnlyRead(permissions.BasePermission):
    """
    Students can only read published content
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return False

# utils.py
from django.contrib.auth.models import User, Group

def create_user_groups():
    """Create admin and student groups if they don't exist"""
    admin_group, created = Group.objects.get_or_create(name='Admin')
    student_group, created = Group.objects.get_or_create(name='Student')
    
    return admin_group, student_group

def assign_user_to_group(user, group_name):
    """Assign user to a specific group"""
    try:
        group = Group.objects.get(name=group_name)
        user.groups.add(group)
        user.save()
        return True
    except Group.DoesNotExist:
        return False

def is_admin_user(user):
    """Check if user is admin"""
    return (user.is_authenticated and 
            (user.is_staff or user.is_superuser or 
             user.groups.filter(name='Admin').exists()))

def is_student_user(user):
    """Check if user is student"""
    return (user.is_authenticated and 
            user.groups.filter(name='Student').exists())