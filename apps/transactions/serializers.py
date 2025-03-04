from uuid import UUID
from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType

from apps.accounts.models import Account
from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.email")
    account = serializers.ReadOnlyField(source = "account.id")
    class Meta:
        model = Transaction
        fields = [
            "id",
            "user",
            "account",
            "type",
            "amount",
            "description",
            "date",
            "category",
            "receiptUrl",
            "isRecurring",
            "recurringInterval",
            "nextRecurringDate",
            "lastProcessed",
            "created_at",
            "updated_at",
        ]
        

    
class CreateTransactionSerializer(serializers.ModelSerializer):
    account_id = serializers.UUIDField()
    class Meta:
        model = Transaction
        fields = [
            "account_id",
            "type",
            "amount",
            "description",
            "receiptUrl",
            "date",
            "category",
            "isRecurring",
            "recurringInterval",
            "nextRecurringDate",
        ]

    def validate(self, data):
        if "receiptUrl" not in data:
            data["receiptUrl"] = ""
        if data["isRecurring"] == False:
            data["recurringInterval"] = ""
        return data 


