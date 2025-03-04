from celery import shared_task
from django.utils import timezone
from config.utils.emails import send_budget_alert
from .models import Budget
from apps.transactions.models import Transaction
from django.db import models



@shared_task(name='check_budget_alerts')
def check_budget_alerts():
    # Récupérer tous les budgets avec leurs utilisateurs et comptes par défaut
    budgets = Budget.objects.select_related('user').prefetch_related(
        'user__account'
    ).filter(user__account__is_default=True)

    for budget in budgets:
        default_account = budget.user.account.filter(is_default=True).first()
        if not default_account:
            continue  # Passer si aucun compte par défaut n'existe

        # Calculer le début du mois en cours
        start_date = timezone.now().replace(
            day=1, hour=0, minute=0, second=0, microsecond=0)

        # Calculer le total des dépenses pour le compte par défaut
        expenses = Transaction.objects.filter(
            user=budget.user,
            account=default_account,
            type=Transaction.Type.EXPENSE,
            date__gte=start_date
        ).aggregate(total_amount=models.Sum('amount'))

        total_expenses = expenses['total_amount'] or 0
        budget_amount = budget.amount
        percentage_used = (total_expenses / budget_amount) * 100

        # Vérifier si une alerte doit être envoyée
        if (
            percentage_used >= 80 and  # Seuil de 80%
            (not budget.last_alert_sent or is_new_month(
                budget.last_alert_sent, timezone.now()))
        ):
            # Envoyer un e-mail
            send_budget_alert(
                budget,
                percentage_used,
                budget_amount,
                total_expenses,
                default_account
            )

            # Mettre à jour la date de la dernière alerte
            budget.last_alert_sent = timezone.now()
            budget.save()


def is_new_month(last_alert_date, current_date):
    """
    Vérifie si la dernière alerte a été envoyée dans un mois différent.
    """
    return (
        last_alert_date.month != current_date.month or
        last_alert_date.year != current_date.year
    )
