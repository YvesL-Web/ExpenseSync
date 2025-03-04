import uuid
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import Account


User = get_user_model()

class Transaction(models.Model):

    class Type(models.TextChoices):
        INCOME = ("income", _("Income"))
        EXPENSE = ("expense", _("Expense"))
    
    class RecurringIntervale(models.TextChoices):
        DAILY = ("daily", _("Daily"))
        WEEKLY = ("weekly",_("Weekly"))
        MONTHLY = ("monthly",_("Monthly"))
        YEARLY = ("yearly",_("Yearly"))

    class Status(models.TextChoices):
        PENDING = ("pending", _("Pending"))
        COMPLETED = ("completed",_("Completed"))
        Failed = ("failed",_("Failed"))

    pkid = models.BigAutoField(primary_key=True, editable=False)
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, related_name="transactions", on_delete=models.CASCADE)
    account = models.ForeignKey(Account,related_name="transactions", on_delete=models.CASCADE)
    type = models.CharField(verbose_name=_("Type"),max_length=10, choices=Type.choices, default=Type.EXPENSE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    date = models.DateTimeField()
    category = models.CharField(max_length=50)
    receiptUrl = models.CharField(blank=True, null=True)
    isRecurring = models.BooleanField(default=False)
    recurringInterval = models.CharField(verbose_name=_("Recurring Intervalle"), max_length=10, choices=RecurringIntervale.choices,blank=True, null=True)
    nextRecurringDate = models.DateTimeField(auto_now=False, auto_now_add=False,blank=True, null=True)
    lastProcessed =  models.DateTimeField(auto_now=False, auto_now_add=False,blank=True, null=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.amount}"



