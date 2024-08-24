# Generated by Django 5.0 on 2024-08-21 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_site', '0006_sitesettingmodel_default_funding_account'),
    ]

    operations = [
        migrations.CreateModel(
            name='SupportedCryptoModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('code', models.CharField(max_length=10)),
                ('status', models.CharField(blank=True, choices=[('active', 'ACTIVE'), ('inactive', 'INACTIVE')], default='active', max_length=10)),
            ],
        ),
    ]
