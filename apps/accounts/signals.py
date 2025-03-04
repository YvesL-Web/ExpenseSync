from .models import Account
from django.db.models.signals import pre_save
from django.dispatch import receiver

# @receiver(pre_save, sender=Account)
# def ensure_at_least_one_default(sender, instance, **kwargs):
#     # Si ce compte est marqué comme défaut, on n'a rien à faire
#     if instance.is_default:
#         return

#     # Vérifier s'il existe déjà un compte par défaut pour cet utilisateur
#     if not Account.objects.filter(user=instance.user, is_default=True).exists():
#         # S'il n'y a aucun compte par défaut, forcer ce compte à être par défaut
#         instance.is_default = True