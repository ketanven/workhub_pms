from django.db import models
from core.models.project import Project
from core.models.task import Task


class TimeEntry(models.Model):
    id = models.BigAutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='time_entries')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='time_entries')
    entry_date = models.DateField()
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(default=0)
    is_manual = models.BooleanField(default=False)
    source = models.CharField(max_length=30, default='timer')
    note = models.TextField(blank=True)
    is_billable = models.BooleanField(default=True)
    hourly_rate_snapshot = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    amount_snapshot = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    local_entry_uuid = models.CharField(max_length=100, blank=True)
    sync_status = models.CharField(max_length=20, default='synced')
    synced_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'time_entries'
        ordering = ['-entry_date', '-created_at']


class TimerSession(models.Model):
    STATUS_RUNNING = 'running'
    STATUS_PAUSED = 'paused'
    STATUS_BREAK = 'break'
    STATUS_STOPPED = 'stopped'

    id = models.BigAutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='timer_sessions')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='timer_sessions')
    started_at = models.DateTimeField()
    paused_at = models.DateTimeField(null=True, blank=True)
    resumed_at = models.DateTimeField(null=True, blank=True)
    stopped_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default=STATUS_RUNNING)
    total_elapsed_seconds = models.PositiveIntegerField(default=0)
    total_break_seconds = models.PositiveIntegerField(default=0)
    started_from = models.CharField(max_length=30, default='web')
    offline_mode = models.BooleanField(default=False)
    local_session_uuid = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'timer_sessions'
        ordering = ['-created_at']


class TimerBreak(models.Model):
    id = models.BigAutoField(primary_key=True)
    timer_session = models.ForeignKey(TimerSession, on_delete=models.CASCADE, related_name='breaks')
    break_started_at = models.DateTimeField()
    break_ended_at = models.DateTimeField(null=True, blank=True)
    break_duration_seconds = models.PositiveIntegerField(default=0)
    reason = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'timer_breaks'
        ordering = ['-created_at']


class OfflineSyncBatch(models.Model):
    id = models.BigAutoField(primary_key=True)
    batch_uuid = models.CharField(max_length=100, unique=True)
    payload_json = models.JSONField(default=dict, blank=True)
    item_count = models.PositiveIntegerField(default=0)
    sync_status = models.CharField(max_length=20, default='pending')
    attempted_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'offline_sync_batches'
        ordering = ['-created_at']
