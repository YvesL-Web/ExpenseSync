import json
import logging 


from datetime import datetime
from celery import shared_task
from django.core.cache import cache
from django.utils import timezone
from django.db.models import Q
from django.db import transaction as db_transaction

from apps.transactions.utils.utilities_functions import calculate_next_recurring_date, is_transaction_due
from .models import Transaction

from google.generativeai import GenerativeModel
from google.api_core.exceptions import GoogleAPIError
from django.db.models import Sum

from django.contrib.auth import get_user_model
from config.utils.emails import send_monthly_report_email


logger = logging.getLogger(__name__)

User = get_user_model()

@shared_task(name="trigger_recurring_transactions")
def trigger_recurring_transactions():
    """
    Tâche pour déclencher les transactions récurrentes.
    """

    # Récupérer les transactions récurrentes à traiter
    recurring_transactions = Transaction.objects.filter(
        isRecurring=True,
        status=Transaction.Status.COMPLETED,
    ).filter(Q(lastProcessed__isnull=True) | Q(nextRecurringDate__lte=datetime.now()))

    # Envoyer chaque transaction récurrente à la tâche de traitement
    for transaction in recurring_transactions:
        process_recurring_transaction.delay(transaction.id)


@shared_task(name="process_recurring_transaction")
def process_recurring_transaction(transaction_id):
    """
    Tâche pour traiter une transaction récurrente.
    """
    user_id = Transaction.objects.get(id=transaction_id).user.id
    cache_key= f"throttle_user_{user_id}"

    # Vérifier le nombre de requêtes dans la dernière minute
    request_count = cache.get(cache_key, 0)
    if request_count >= 10:  # Limite de 10 requêtes par minute
        return {"error": "Rate limit exceeded"}
    
    # Incrémenter le compteur de requêtes
    cache.set(cache_key, request_count + 1, timeout=60)

    try:
        transaction = Transaction.objects.get(id=transaction_id)
        # vérifier si la transaction est due
        if not is_transaction_due(transaction):
            return
        
        # Créer une nouvelle transaction et mettre à jour le solde du compte
        with db_transaction.atomic():
            # Créer une nouvelle transaction
            new_transaction = Transaction.objects.create(
                user = transaction.user,
                account = transaction.account,
                type = transaction.type,
                amount = transaction.amount,
                category= transaction.category,
                description = f"{transaction.description} (recurring).",
                date = timezone.now(),
                isRecurring = False,
                status=Transaction.Status.PENDING
            )

            # Mettre à jour le solde du compte
            balance_change = 0
            if transaction.type == "expense":
                balance_change -= transaction.amount
            else:
                balance_change += transaction.amount
            
            transaction.account.balance += balance_change
            transaction.account.save()

            # Mettre à jour la date de dernier traitement et la prochaine date de récurrence
            transaction.lastProcessed = timezone.now()
            transaction.nextRecurringDate = calculate_next_recurring_date(transaction)
            transaction.save()
    except Transaction.DoesNotExist:
        pass


@shared_task(name="generate_monthly_reports")
def generate_monthly_reports():
    """
    Tâche pour générer des rapports mensuels pour tous les utilisateurs 
    """
    users = User.objects.all()
    for user in users:
        generate_user_monthly_report.delay(user.id)
    
    return {"Processed": users.count()}


@shared_task(name="generate_user_monthly_report")
def generate_user_monthly_report(user_id):
    """
    Tâche pour générer un rapport mensuel pour un utilisateur spécifique
    """
    try:
        user = User.objects.get(id=user_id)
        last_month = timezone.now() - timezone.timedelta(days=30)

        # récupérer les satistiques mensuelles
        stats = get_monthly_stats(user, last_month)
        month_name = last_month.strftime("%B")

        # Générer des insights avec Gemini
        insights = generate_financial_insights(stats, month_name)

        # Envoyer un e-mail avec le rapport
        send_monthly_report_email(user, stats, month_name, insights)

    except User.DoesNotExist:
        pass


def get_monthly_stats(user, month):
    """
    Récupérer les statistiques mensuelles pour un utilisateur
    """
    transactions = Transaction.objects.filter(
        user = user,
        date__month = month.month,
        date__year = month.year
    )

    total_income = transactions.filter(type="income").aggregate(Sum("amount"))["amount__sum"] or 0
    total_expenses = transactions.filter(type="expense").aggregate(Sum("amount"))["ammount__sum"] or 0
    by_category = transactions.filter(type="expense").values("category").annotate(total=Sum("amount"))

    return {
        "total_incomes": total_income,
        "total_expenses": total_expenses,
        "by_category": {
            item["category"]: item["total"] for item in by_category
        },
    }


def generate_financial_insights(stats, month):
    """
    Génère des insights financières avec Gemini
    """
    model = GenerativeModel("gemini-1.5-flash")
    prompt = f"""
        Analyze this financial data and provide 3 concise, actionable insights.
        Focus on spending patterns and practical advice.
        Keep it friendly and conversational.

        Financial Data for {month}:
        - Total Income: ${stats["total_income"]}
        - Total Expenses: ${stats["total_expenses"]}
        - Net Income: ${stats["total_income"] - stats["total_expenses"]}
        - Expense Categories: {", ".join([f"{k}: ${v}" for k, v in stats["by_category"].items()])}
        
        Format the response as a JSON array of strings, like this:
        ["insight 1", "insight 2", "insight 2"]
    """
    try:
        response = model.generate_content(prompt)
        text = response.text.replace("```json","").replace("```","").strip()
        return json.loads(text)
    except Exception as e:
        logger.error(f"Error generating insights: {e}")
        return [
            "Your highest expense category this month might need attention.",
            "Consider setting up a budget for better financial management.",
            "Track your recurring expenses to identify potential savings.",
        ]
    
