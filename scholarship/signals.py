# from django.db.models.signals import post_save, pre_save
# from django.dispatch import receiver
# from django.contrib.auth.models import User
# from .models import ScholarshipApplication, UserProfile
# from .utils import notify_admins_new_application, notify_student_status_update


# @receiver(post_save, sender=ScholarshipApplication)
# def handle_new_application(sender, instance, created, **kwargs):
#     """Send notifications when new application is created"""
#     if created:
#         notify_admins_new_application(instance)


# @receiver(pre_save, sender=ScholarshipApplication)
# def track_application_status_change(sender, instance, **kwargs):
#     """Track status changes for notifications"""
#     if instance.pk:  # Only for existing instances
#         try:
#             old_instance = ScholarshipApplication.objects.get(pk=instance.pk)
#             instance._old_status = old_instance.status
#         except ScholarshipApplication.DoesNotExist:
#             instance._old_status = None
#     else:
#         instance._old_status = None


# @receiver(post_save, sender=ScholarshipApplication)
# def handle_status_update(sender, instance, created, **kwargs):
#     """Send notifications when application status is updated"""
#     if not created and hasattr(instance, '_old_status'):
#         old_status = instance._old_status
#         if old_status and old_status != instance.status:
#             notify_student_status_update(instance, old_status) sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     """Create user profile when user is created"""
#     if created:
#         UserProfile.objects.create(user=instance)


# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     """Save user profile when user is saved"""
#     if hasattr(instance, 'profile'):
#         instance.profile.save()


# @receiver(post_save,