# Generated by Django 5.0 on 2024-08-28 06:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_site', '0014_alter_sitesettingmodel_referral_payment_before_bonus'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitesettingmodel',
            name='minimum_trade_time',
            field=models.IntegerField(default=1),
        ),
    ]
