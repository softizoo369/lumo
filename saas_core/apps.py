from django.apps import AppConfig

class SaasCoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'saas_core'

    def ready(self):
        # অটো-অনবোর্ডিং সিগন্যালটি লোড করা হচ্ছে
        import saas_core.signals