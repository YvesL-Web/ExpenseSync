import logging

from uuid import UUID
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied, ValidationError
from .models import Account
from .serializers import AccountSerializer, AccountWithTransactions, BaseAccountSerializer
from config.utils.renderers import GenericJSONRenderer
from rest_framework.response import Response


logger = logging.getLogger(__name__)

# Create your views here.
class AccountCreateApiView(generics.CreateAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [GenericJSONRenderer]
    object_label = "account"

    def perform_create(self, serializer):
        serializer.save()


class MyAccountsListApiView(generics.ListAPIView):
    queryset = Account.objects.all()
    serializer_class = BaseAccountSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [GenericJSONRenderer]
    object_label = "My_accounts"

    def get_queryset(self):
       user = self.request.user
       return Account.objects.filter(user=user)
   

class UpdateDefaultAccount(APIView):
    permission_classes= [permissions.IsAuthenticated]
    renderer_classes = [GenericJSONRenderer]
    # object_label = "account"
    
    def get_object(self,account_id):
        try:
            UUID(str(account_id))
            return Account.objects.get(id=account_id)
        except (ValueError, ValidationError) as e:
            logger.error(str(e))
            return None
        except Account.DoesNotExist:
            return None
    
    def patch(self, request, account_id):
        account = self.get_object(account_id)
        if account is None:
            return Response({"detail":"Account not found"}, status=status.HTTP_404_NOT_FOUND)

        if account.user != self.request.user:
            raise PermissionDenied("You do not have permissions.")
        serializer = BaseAccountSerializer(account, data=request.data)
        if serializer.is_valid():
            user = account.user
            is_default = request.data.get("is_default", False)
            if not is_default:
                if not Account.objects.filter(user=user, is_default=True).exclude(id=account_id).exists():
                    return Response({"detail": "At least one account must be marked as default."}, status=status.HTTP_400_BAD_REQUEST)
            if serializer.validated_data["is_default"] == True:
                existing_accounts = Account.objects.filter(user=self.request.user)
                existing_accounts.update(is_default=False)
            serializer.save()
            return Response({"detail":"Account updated"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class GetAccountWithTransaction(generics.RetrieveAPIView):
    queryset = Account.objects.all()
    permission_classes= [permissions.IsAuthenticated]
    serializer_class = AccountWithTransactions
    lookup_field = "id"

