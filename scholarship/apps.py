from django.apps import AppConfig


class ScholarshipConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scholarship'

    def ready(self):
        import scholarship.signals
