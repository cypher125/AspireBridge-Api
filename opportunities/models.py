from django.db import models
import uuid
from users.models import User

class Opportunity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    organization = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    type = models.CharField(
        max_length=50,
        choices=[
            ('internship', 'Internship'),
            ('job', 'Job'),
            ('project', 'Project'),
            ('research', 'Research')
        ]
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Draft'),
            ('active', 'Active'),
            ('closed', 'Closed'),
            ('archived', 'Archived')
        ],
        default='draft'
    )
    requirements = models.JSONField(default=list)  # List of required skills/qualifications
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_opportunities')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    application_deadline = models.DateTimeField()
    start_date = models.DateField()
    duration = models.CharField(max_length=100)
    compensation = models.CharField(max_length=255, blank=True)
    required_documents = models.JSONField(default=list)  # List of required document types
    views_count = models.IntegerField(default=0)
    applications_count = models.IntegerField(default=0)
    saved_by = models.ManyToManyField(User, related_name='saved_opportunities', blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['type']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['application_deadline']),
        ]

    def __str__(self):
        return self.title

    def update_counts(self):
        self.applications_count = self.applications.count()
        self.save(update_fields=['applications_count']) 