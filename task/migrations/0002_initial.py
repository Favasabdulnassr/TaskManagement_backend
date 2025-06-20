# Generated by Django 5.2.2 on 2025-06-10 06:31

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('task', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['user', 'status'], name='tasks_user_id_a53e17_idx'),
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['scheduled_date'], name='tasks_schedul_49269d_idx'),
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['priority'], name='tasks_priorit_a9efa1_idx'),
        ),
    ]
