from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.db import transaction
from apps.accounts.models import Account
from apps.transactions.serializers import TransactionSerializer


User = get_user_model()

class AccountSerializer(serializers.ModelSerializer):
    balance = serializers.DecimalField(max_digits=10, decimal_places=2)
    user = serializers.ReadOnlyField(source="user.email")
    is_default = serializers.BooleanField()
    class Meta:
        model = Account
        fields = [
            "user",
            "name",
            "type",
            "balance",
            "is_default"
        ]

    def validate_balance(self,value):
        if value <= 0:
            raise serializers.ValidationError("Balance cannot be smaller or equal to 0.")
        return value

    def create(self, validated_data) :
        user = self.context["request"].user
        with transaction.atomic(): # Utilisation d'une transaction pour garantir l'intégrité des données
            #  Vérifier si l'utilisateur a déjà des comptes bancaires
            existing_accounts = Account.objects.filter(user=user)
            if not existing_accounts:
                is_default = True
                new_account = Account.objects.create(
                    user = user,
                    name = validated_data.get("name"),
                    type = validated_data.get("type"),
                    balance = validated_data.get("balance"),
                    is_default = is_default,
                )
                return new_account

            if validated_data.get("is_default") == True :
                existing_accounts.update(is_default=False)
                
            account = Account.objects.create(
               user = user,
                **validated_data
            )
            return account


class BaseAccountSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.email")
    class Meta:
        model = Account
        fields = [
            "id",
            "user",
            "name",
            "type",
            "balance",
            "is_default",
            "created_at",
            "updated_at"
        ]

class AccountWithTransactions(BaseAccountSerializer):
    transactions = TransactionSerializer(many=True, read_only=True)
    class Meta(BaseAccountSerializer.Meta):
       fields = BaseAccountSerializer.Meta.fields + ["transactions"]
