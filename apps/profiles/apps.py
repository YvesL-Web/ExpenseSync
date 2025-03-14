from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _  # make app available in different languages

class ProfilesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.profiles'
    verbose_name= _("Profiles")

    def ready(self) -> None:
        import apps.profiles.signals
