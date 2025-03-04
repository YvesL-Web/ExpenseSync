from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _  # make app available in different languages

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'
    verbose_name= _("Accounts")

    # def ready(self) -> None:
    #     import apps.accounts.signals
