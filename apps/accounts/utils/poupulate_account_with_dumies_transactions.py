from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from datetime import timedelta
from django.utils import timezone
import random
from decimal import Decimal
from ..models import Account
from apps.transactions.models import Transaction

class SeedTransactionsView(APIView):
    http_method_names = ["post"]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        account = Account.objects.get(user=request.user)
        ACCOUNT_ID = account.id
        USER = request.user

        print(f"USER: {request.user}")
        print(f"Account: {account.id}")

        CATEGORIES = {
            'income': [
                {'name': 'salary', 'range': [5000, 8000]},
                {'name': 'freelance', 'range': [1000, 3000]},
                {'name': 'investments', 'range': [500, 2000]},
                {'name': 'other-income', 'range': [100, 1000]},
            ],
            'expense': [
                {'name': 'housing', 'range': [1000, 2000]},
                {'name': 'transportation', 'range': [100, 500]},
                {'name': 'groceries', 'range': [200, 600]},
                {'name': 'utilities', 'range': [100, 300]},
                {'name': 'entertainment', 'range': [50, 200]},
                {'name': 'food', 'range': [50, 150]},
                {'name': 'shopping', 'range': [100, 500]},
                {'name': 'healthcare', 'range': [100, 1000]},
                {'name': 'education', 'range': [200, 1000]},
                {'name': 'travel', 'range': [500, 2000]},
            ],
        }

        def get_random_amount(min_amount, max_amount):
            return Decimal(random.uniform(min_amount, max_amount)).quantize(Decimal('0.01'))

        def get_random_category(type):
            categories = CATEGORIES[type]
            category = random.choice(categories)
            amount = get_random_amount(category['range'][0], category['range'][1])
            return {'category': category['name'], 'amount': amount}

        try:
            transactions = []
            total_balance = Decimal('0.0')

            for i in range(0, 50):
               
                date = timezone.now() - timedelta(days=i)

                transactions_per_day = random.randint(1, 3)

                for _ in range(transactions_per_day):
                    type = 'income' if random.random() < 0.4 else 'expense'
                    category_data = get_random_category(type)
                    amount = category_data['amount']
                    category = category_data['category']

                    transaction = {
                        'type': type,
                        'amount': amount,
                        'description': f"{'Received' if type == 'income' else 'Paid for'} {category}",
                        'date': date,
                        'category': category,
                        # 'status': 'COMPLETED',
                        'user': request.user,
                        # 'account': account,
                    }
                    
                    total_balance += amount if type == 'income' else -amount
                    transactions.append(transaction)

            # account, created = Account.objects.get_or_create(id=ACCOUNT_ID, defaults={'balance': total_balance})
            account, created = Account.objects.get_or_create(id=ACCOUNT_ID)

            # Clear existing transactions
            Transaction.objects.filter(account=account).delete()

            # Insert new transactions
            Transaction.objects.bulk_create([
                Transaction(**transaction, account=account) for transaction in transactions
            ])

            # Update account balance
            account.balance = total_balance
            account.save()

            return Response({
                'success': True,
                'message': f'Created {len(transactions)} transactions',
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)