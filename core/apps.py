from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
def ready(self):
        import core.signals  # Asegúrate de crear un archivo signals.py si usas uno