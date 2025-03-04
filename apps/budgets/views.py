from django.utils import timezone
import logging

from uuid import UUID
from django.db.models import Sum
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied, ValidationError

from .models import Budget
from apps.accounts.models import Account    
from apps.transactions.models import Transaction
from config.utils.renderers import GenericJSONRenderer
from rest_framework.response import Response

logger = logging.getLogger(__name__)

class GetCurrentBudgetView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [GenericJSONRenderer]
    object_label = "budget"

    def get_default_account(self):
        user = self.request.user
        try:
            return Account.objects.get(user=user, is_default=True)
        except Account.DoesNotExist:
            return None
        except (ValueError, ValidationError) as e:
            logger.error(str(e))
            return None
        

    def get(self, request):
        user = self.request.user

        # Get the user's budget
        try:
            budget = Budget.objects.get(user=user)
        except Budget.DoesNotExist:
            budget = None
        
        # Calculate current month's expenses
        today = timezone.now()
        start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_of_month = start_of_month.replace(month=start_of_month.month + 1) - timezone.timedelta(days=1)

   
        account = self.get_default_account()
        if account is None:
            return Response({"detail":"No default Account found."}, status=status.HTTP_404_NOT_FOUND)


        expenses = Transaction.objects.filter(
            user = user,
            type = Transaction.Type.EXPENSE,
            date__gte=start_of_month,
            date__lte=end_of_month,
            account=account,
        ).aggregate(total_expenses=Sum('amount'))
        
        current_expenses = expenses['total_expenses'] or 0

        return Response(
            {
                "amount": float(budget.amount) if budget else None,
                "current_expenses": float(current_expenses),
            },
            status=status.HTTP_200_OK,
        )
    

class UpdateBudgetView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [GenericJSONRenderer]
    def patch(self, request):
        
        # Get the user
        user = self.request.user

        # Get the amount from the request
        amount = request.data.get('amount')
        if amount is None:
            return Response(
                {"success": False, "error": "Amount is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            actual_budget_obj = Budget.objects.get(user=user) 
        except:
            actual_budget_obj = None
        
        if actual_budget_obj is not None:
            actual_budget = actual_budget_obj.amount
            if actual_budget == amount:
                return Response(
                    {"success": False, "detail": "Amount is the same as the current budget"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # Update the budget
            actual_budget_obj.amount = amount
            actual_budget_obj.save()
    
            return Response(
                {
                    "success": True,
                    "data": {
                        "amount": float(actual_budget_obj.amount),
                    },
                },
                status=status.HTTP_200_OK,
            )
        else:
            budget = Budget.objects.create(user=user, amount=amount)
            return Response(
                {
                    "success": True,
                    "data": {
                        "amount": float(budget.amount),
                    },
                },
                status=status.HTTP_201_CREATED,
            )