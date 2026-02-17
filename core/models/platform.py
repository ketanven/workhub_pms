import uuid
from django.db import models


class Notification(models.Model):
    id = models.BigAutoField(primary_key=True)
    notification_type = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    message = models.TextField()
    entity_type = models.CharField(max_length=50, blank=True)
    entity_id = models.CharField(max_length=100, blank=True)
    severity = models.CharField(max_length=20, default='info')
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    action_url = models.CharField(max_length=255, blank=True)
    metadata_json = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']


class File(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    storage_disk = models.CharField(max_length=50, default='local')
    path = models.CharField(max_length=255)
    original_name = models.CharField(max_length=255)
    mime_type = models.CharField(max_length=100, blank=True)
    extension = models.CharField(max_length=20, blank=True)
    size_bytes = models.BigIntegerField(default=0)
    checksum = models.CharField(max_length=128, blank=True)
    visibility = models.CharField(max_length=20, default='private')
    status = models.CharField(max_length=20, default='uploaded')
    metadata_json = models.JSONField(default=dict, blank=True)
    uploaded_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'files'


class WorkspaceSetting(models.Model):
    id = models.BigAutoField(primary_key=True)
    currency = models.CharField(max_length=10, default='USD')
    timezone = models.CharField(max_length=100, default='UTC')
    week_start_day = models.CharField(max_length=20, default='monday')
    default_hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    invoice_due_days_default = models.PositiveIntegerField(default=7)
    invoice_tax_default = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    invoice_prefix_default = models.CharField(max_length=20, default='INV')
    date_format = models.CharField(max_length=30, default='YYYY-MM-DD')
    time_format = models.CharField(max_length=30, default='24h')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'workspace_settings'
