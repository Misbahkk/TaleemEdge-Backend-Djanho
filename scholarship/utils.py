from .models import Notification


def send_notification(user, title, message, notification_type, scholarship=None, application=None):
    """
    Utility function to send notifications to users
    """
    notification = Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type,
        scholarship=scholarship,
        application=application
    )
    
    # Here you can add additional logic like:
    # - Send email notifications
    # - Send push notifications
    # - Send SMS
    # - Real-time notifications via WebSockets
    
    return notification


def get_user_unread_notifications_count(user):
    """
    Get count of unread notifications for a user
    """
    return Notification.objects.filter(user=user, is_read=False).count()


def notify_admins_new_application(application):
    """
    Notify all admin users about a new scholarship application
    """
    from django.contrib.auth.models import User
    
    admin_users = User.objects.filter(profile__role='admin')
    
    for admin in admin_users:
        send_notification(
            user=admin,
            title="New Scholarship Application",
            message=f"New application received for '{application.scholarship.title}' from {application.student.get_full_name() or application.student.username}",
            notification_type='scholarship_application',
            scholarship=application.scholarship,
            application=application
        )


def notify_student_status_update(application, old_status):
    """
    Notify student when their application status is updated
    """
    if application.status != old_status:
        status_messages = {
            'approved': 'Congratulations! Your application has been approved.',
            'rejected': 'Unfortunately, your application has been rejected.',
            'under_review': 'Your application is currently under review.',
            'pending': 'Your application is pending review.'
        }
        
        send_notification(
            user=application.student,
            title=f"Application Status Updated",
            message=f"Your application for '{application.scholarship.title}' has been updated. Status: {application.get_status_display()}. {status_messages.get(application.status, '')}",
            notification_type='scholarship_status_update',
            scholarship=application.scholarship,
            application=application
        )