# Generated by Django 5.0.4 on 2024-04-21 01:46

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paper', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
