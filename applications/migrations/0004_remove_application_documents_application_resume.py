# Generated by Django 5.1.4 on 2025-01-19 12:06

import applications.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0003_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='application',
            name='documents',
        ),
        migrations.AddField(
            model_name='application',
            name='resume',
            field=models.FileField(blank=True, null=True, upload_to=applications.models.resume_upload_path),
        ),
    ]
