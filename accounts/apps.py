from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        # অ্যাকাউন্টের সিগন্যালগুলো লোড করা হবে (যদি ভবিষ্যতে অ্যাড করি)
        pass