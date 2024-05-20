# Generated by Django 5.0.4 on 2024-04-10 03:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_alter_user_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('student', 'student'), ('teacher', 'teacher')], default='student', max_length=16, verbose_name='role'),
        ),
    ]
