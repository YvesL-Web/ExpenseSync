# Generated by Django 4.2.11 on 2025-02-20 10:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('budgets', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='budget',
            old_name='lastAlertSent',
            new_name='last_alert_sent',
        ),
    ]
