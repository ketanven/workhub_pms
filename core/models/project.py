import uuid
from django.db import models
from django.contrib.auth import get_user_model
from core.models.client import Client

User = get_user_model()


class Project(models.Model):
    STATUS_PLANNED = 'planned'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_ON_HOLD = 'on_hold'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELED = 'canceled'

    PRIORITY_LOW = 'low'
    PRIORITY_MEDIUM = 'medium'
    PRIORITY_HIGH = 'high'
    PRIORITY_URGENT = 'urgent'

    BILLING_HOURLY = 'hourly'
    BILLING_FIXED = 'fixed'

    STATUS_CHOICES = [
        (STATUS_PLANNED, 'Planned'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_ON_HOLD, 'On Hold'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELED, 'Canceled'),
    ]

    PRIORITY_CHOICES = [
        (PRIORITY_LOW, 'Low'),
        (PRIORITY_MEDIUM, 'Medium'),
        (PRIORITY_HIGH, 'High'),
        (PRIORITY_URGENT, 'Urgent'),
    ]

    BILLING_CHOICES = [
        (BILLING_HOURLY, 'Hourly'),
        (BILLING_FIXED, 'Fixed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, related_name='projects', on_delete=models.CASCADE)
    client = models.ForeignKey(Client, related_name='projects', on_delete=models.CASCADE)

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PLANNED)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM)

    billing_type = models.CharField(max_length=20, choices=BILLING_CHOICES, default=BILLING_HOURLY)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fixed_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, blank=True)

    estimated_hours = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    progress_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)

    notes = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    is_active = models.BooleanField(default=True)
    archived_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['user', 'name']),
            models.Index(fields=['client', 'status']),
        ]

    def __str__(self):
        return f"{self.name} ({self.user.email})"
