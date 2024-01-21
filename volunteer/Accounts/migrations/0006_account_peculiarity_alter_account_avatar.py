# Generated by Django 4.0 on 2023-08-11 13:01

import Accounts.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0005_account_token_alter_account_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='peculiarity',
            field=models.CharField(choices=[('handicapped', 'инвалидность'), ('autism', 'аутизм')], max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='account',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to=Accounts.models.f),
        ),
    ]