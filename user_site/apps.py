from django.apps import AppConfig


class UserSiteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user_site'

    def ready(self):
        import user_site.signals
