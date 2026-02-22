from django.db import models
from .project import Project
from .task import Task


class TimeEntry(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)

    entry_date = models.DateField()

    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    duration_seconds = models.IntegerField(default=0)

    is_manual = models.BooleanField(default=False)
    source = models.CharField(max_length=50, default="timer")

    note = models.TextField(null=True, blank=True)
    is_billable = models.BooleanField(default=True)

    hourly_rate_snapshot = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    amount_snapshot = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    local_entry_uuid = models.CharField(max_length=100, null=True, blank=True)
    sync_status = models.CharField(max_length=50, default="synced")
    synced_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"TimeEntry {self.id} - Task {self.task_id}"


class TimerSession(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)

    started_at = models.DateTimeField()
    paused_at = models.DateTimeField(null=True, blank=True)
    resumed_at = models.DateTimeField(null=True, blank=True)
    stopped_at = models.DateTimeField(null=True, blank=True)

    status = models.CharField(max_length=50, default="running")

    total_elapsed_seconds = models.IntegerField(default=0)
    total_break_seconds = models.IntegerField(default=0)

    started_from = models.CharField(max_length=50, default="web")
    offline_mode = models.BooleanField(default=False)

    local_session_uuid = models.CharField(max_length=100, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"TimerSession {self.id} - Task {self.task_id}"


class TimerBreak(models.Model):
    timer_session = models.ForeignKey(TimerSession, on_delete=models.CASCADE)

    break_started_at = models.DateTimeField()
    break_ended_at = models.DateTimeField(null=True, blank=True)

    break_duration_seconds = models.IntegerField(default=0)

    reason = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-break_started_at"]

    def __str__(self):
        return f"Break {self.id} - Session {self.timer_session_id}"


class OfflineSyncBatch(models.Model):
    batch_uuid = models.CharField(max_length=100)

    payload_json = models.JSONField()
    item_count = models.IntegerField(default=0)

    sync_status = models.CharField(max_length=50, default="pending")

    attempted_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    error_message = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"OfflineBatch {self.batch_uuid}"