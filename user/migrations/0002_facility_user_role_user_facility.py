# Generated by Django 4.2.7 on 2024-04-03 04:30

from django.db import migrations, models
import django.db.models.deletion
import user.models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Facility',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('invitation_code', models.IntegerField(default=user.models.new_invitation_code, unique=True, verbose_name='invitation code')),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.CharField(default='student', max_length=16, verbose_name='role'),
        ),
        migrations.AddField(
            model_name='user',
            name='facility',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='user.facility'),
        ),
    ]
