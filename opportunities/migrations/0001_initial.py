# Generated by Django 5.1.4 on 2025-01-18 10:46

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Opportunity',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('organization', models.CharField(max_length=255)),
                ('location', models.CharField(max_length=255)),
                ('type', models.CharField(choices=[('internship', 'Internship'), ('job', 'Job'), ('project', 'Project'), ('research', 'Research')], max_length=50)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('active', 'Active'), ('closed', 'Closed'), ('archived', 'Archived')], default='draft', max_length=20)),
                ('requirements', models.JSONField(default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('application_deadline', models.DateTimeField()),
                ('start_date', models.DateField()),
                ('duration', models.CharField(max_length=100)),
                ('compensation', models.CharField(blank=True, max_length=255)),
                ('required_documents', models.JSONField(default=list)),
                ('views_count', models.IntegerField(default=0)),
                ('applications_count', models.IntegerField(default=0)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
