# Generated by Django 5.0 on 2024-08-28 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_site', '0023_usertrademodel'),
    ]

    operations = [
        migrations.AddField(
            model_name='usertrademodel',
            name='status',
            field=models.CharField(blank=True, default='open', max_length=10),
        ),
    ]
