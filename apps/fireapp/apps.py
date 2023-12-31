from django.apps import AppConfig


class FireappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.fireapp'
    verbose_name = 'Firebase Connection App'
    def ready(self):
        import apps.fireapp.signals