# Generated by Django 4.2.11 on 2025-02-06 16:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='account',
            old_name='isDefault',
            new_name='is_default',
        ),
    ]
