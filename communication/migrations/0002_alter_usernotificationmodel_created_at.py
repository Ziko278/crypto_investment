# Generated by Django 5.0 on 2024-08-30 08:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usernotificationmodel',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
