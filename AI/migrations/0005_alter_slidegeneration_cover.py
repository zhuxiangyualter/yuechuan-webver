# Generated by Django 5.0.4 on 2024-04-12 06:20

import AI.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AI', '0004_slidegeneration_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='slidegeneration',
            name='cover',
            field=models.ImageField(upload_to=AI.models.Rename('ai/slides/cover/')),
        ),
    ]
