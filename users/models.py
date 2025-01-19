from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    role = models.CharField(
        max_length=20,
        choices=[
            ('student', 'Student'),
            ('administrator', 'Administrator')
        ],
        default='student'
    )
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.',
    )
    
    matriculation_number = models.CharField(max_length=50, blank=True)
    course = models.CharField(max_length=255, blank=True)
    year_of_study = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    organization_details = models.TextField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True)
    join_date = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=255, blank=True)
    completion_rate = models.IntegerField(default=0)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'name']

    class Meta:
        ordering = ['-join_date']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['-join_date'])
        ]

    def calculate_completion_rate(self):
        fields = ['name', 'email', 'phone_number', 'location', 'course', 
                 'year_of_study', 'description', 'profile_picture']
        completed = sum(1 for field in fields if getattr(self, field))
        self.completion_rate = int((completed / len(fields)) * 100)
        self.save(update_fields=['completion_rate'])
        return self.completion_rate 