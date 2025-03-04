import logging

from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from apps.accounts.models import Account
from apps.budgets.models import Budget
from config.settings.base import SITE_NAME, DEFAULT_FROM_EMAIL


logger = logging.getLogger(__name__)


def send_budget_alert(budget: Budget,percentage_used,budget_amount,total_expenses,default_account:Account) -> None:
    """Send an email to the user when their budget is exceeded."""
    site_name = SITE_NAME
    try:
        subject = "Budget Alert"
        context = {
            'first_name': budget.user.first_name,
            'last_name': budget.user.last_name,
            'percentage_used': round(percentage_used, 1),
            'budget_amount': round(budget_amount, 1),
            'total_expenses': round(total_expenses, 1),
            'account_name': default_account.name,
            "site_name": site_name
        }

        html_email = render_to_string('emails/budget_alert.html', context)
        text_email = strip_tags(html_email)
        from_email = DEFAULT_FROM_EMAIL
        to = [budget.user.email]
        email = EmailMultiAlternatives(subject, text_email, from_email, to)

        email.attach_alternative(html_email, "text/html")
        email.send()
    except Exception as e:
        logger.error(
            f"Failed to send budget alert email for issue!", exc_info=True)


def send_monthly_report_email(user, stats, month, insights):
    """
    Envoie un e-mail avec le rapport mensuel.
    """
    site_name = SITE_NAME
    subject = f"Your Monthly Financial Report - {month}."
    html_message = render_to_string("emails/monthly_report.html", {
        "first_name": user.first_name,
        "last_name": user.last_name,
        "stats":stats,
        "month": month,
        "insights": insights,
        "site": site_name,
    })
    plain_message = strip_tags(html_message)
    send_mail(
        subject=subject,
        message=plain_message,
        recipient_list=[user.email],
        html_message= html_message
    )