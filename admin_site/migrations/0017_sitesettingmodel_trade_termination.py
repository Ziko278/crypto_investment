# Generated by Django 5.0 on 2024-08-28 15:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_site', '0016_sitesettingmodel_minimum_trade_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitesettingmodel',
            name='trade_termination',
            field=models.BooleanField(default=True),
        ),
    ]
