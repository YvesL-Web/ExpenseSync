import logging
from typing import Any, Type

from django.db.models.base import Model
from django.db.models.signals import post_save
from django.dispatch import receiver

# from config.settings.base import AUTH_USER_MODEL
from apps.profiles.models import Profile
from django.contrib.auth import get_user_model

User = get_user_model()

logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def create_user_profile(sender: Type[Model], instance:Model, created:bool, **kwargs: Any) -> None:
    
    if created:
        Profile.objects.create(user=instance)
        logger.info(f"Profile created for {instance.first_name} {instance.last_name}.")
    else:
        # logger.info(f"Profile already exists for {instance.first_name} {instance.last_name}.")
        pass