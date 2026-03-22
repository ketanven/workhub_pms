from django.db import models
import uuid

class Permission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50) # e.g. "Read", "Write"
    code = models.CharField(max_length=100, unique=True) # e.g. "dashboard_read"
    group_name = models.CharField(max_length=100) # e.g. "Dashboard"
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.group_name} - {self.name}"

class Role(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    permissions = models.ManyToManyField(Permission, blank=True, related_name='roles')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
