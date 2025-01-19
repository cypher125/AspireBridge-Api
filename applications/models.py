from django.db import models
import uuid
from users.models import User
from opportunities.models import Opportunity

def resume_upload_path(instance, filename):
    # Upload to MEDIA_ROOT/resumes/user_id/filename
    return f'resumes/{instance.user.id}/{filename}'

class Application(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('under_review', 'Under Review'),
            ('shortlisted', 'Shortlisted'),
            ('accepted', 'Accepted'),
            ('rejected', 'Rejected'),
            ('withdrawn', 'Withdrawn')
        ],
        default='pending'
    )
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cover_letter = models.TextField()
    resume = models.FileField(upload_to=resume_upload_path, null=True, blank=True)
    admin_notes = models.TextField(blank=True)
    interview_date = models.DateTimeField(null=True, blank=True)
    interview_feedback = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True)

    class Meta:
        ordering = ['-applied_at']
        unique_together = ['user', 'opportunity']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['-applied_at']),
            models.Index(fields=['user']),
            models.Index(fields=['opportunity']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.opportunity.title}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.opportunity.update_counts() 