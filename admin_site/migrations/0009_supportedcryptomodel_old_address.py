# Generated by Django 5.0 on 2024-08-21 20:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_site', '0008_supportedcryptomodel_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='supportedcryptomodel',
            name='old_address',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
