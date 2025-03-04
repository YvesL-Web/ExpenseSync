from django.db import models
import uuid
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _


User = get_user_model()

class Budget(models.Model):

    pkid = models.BigAutoField(primary_key=True, editable=False)
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, related_name="budget", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    last_alert_sent = models.DateTimeField(auto_now=False, auto_now_add=False,blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)