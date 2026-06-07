from django.apps import AppConfig


class FinanceConfig(AppConfig):
    name = 'finance'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        # Import signal handlers to ensure they are registered
        try:
            import finance.signals  # noqa: F401
        except Exception:
            pass
