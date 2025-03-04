from datetime import timedelta, datetime
from django.utils import timezone
from apps.transactions.models import Transaction


def calculate_next_recurring_date(transaction: Transaction) -> None | datetime:
    """
    Calcule la prochaine date de récurrence en fonction de l'intervalle.
    """
    if not transaction.recurringInterval:
        return None

    interval = transaction.recurringInterval
    last_processed_date = transaction.lastProcessed

    if interval.lower() == 'daily':
        return last_processed_date + timezone.timedelta(days=1)
    elif interval.lower() == 'weekly':

        return last_processed_date + timezone.timedelta(weeks=1)
    elif interval.lower() == 'monthly':
        return last_processed_date + timezone.timedelta(days=30)  # Approximation
    elif interval.lower() == 'yearly':
        return last_processed_date + timezone.timedelta(days=365)  # Approximation
    else:
        return None
    

def is_transaction_due(transaction):
    """
    Vérifie si une transaction récurrente est due.
    """
    if not transaction.isRecurring:
        return False

    current_date = timezone.now()
    if transaction.nextRecurringDate and transaction.nextRecurringDate > current_date:
        return False

    return True