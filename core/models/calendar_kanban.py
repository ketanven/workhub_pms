from django.db import models
from core.models.project import Project
from core.models.task import Task


class CalendarEvent(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    event_type = models.CharField(max_length=50, default='custom')
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    all_day = models.BooleanField(default=False)
    timezone = models.CharField(max_length=100, default='UTC')
    location = models.CharField(max_length=200, blank=True)
    color = models.CharField(max_length=20, blank=True)
    source_type = models.CharField(max_length=50, blank=True)
    source_id = models.CharField(max_length=100, blank=True)
    reminder_minutes_before = models.IntegerField(null=True, blank=True)
    recurrence_rule = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, default='scheduled')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'calendar_events'
        ordering = ['start_at']


class CalendarEventLink(models.Model):
    id = models.BigAutoField(primary_key=True)
    calendar_event = models.ForeignKey(CalendarEvent, on_delete=models.CASCADE, related_name='links')
    entity_type = models.CharField(max_length=50)
    entity_id = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'calendar_event_links'


class KanbanBoard(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=20, blank=True)
    icon = models.CharField(max_length=50, blank=True)
    visibility = models.CharField(max_length=20, default='private')
    sort_order = models.PositiveIntegerField(default=0)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'kanban_boards'
        ordering = ['sort_order', 'id']


class KanbanColumn(models.Model):
    id = models.BigAutoField(primary_key=True)
    board = models.ForeignKey(KanbanBoard, on_delete=models.CASCADE, related_name='columns')
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=20, blank=True)
    limit_count = models.PositiveIntegerField(null=True, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_done_column = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'kanban_columns'
        ordering = ['sort_order', 'id']


class KanbanCard(models.Model):
    id = models.BigAutoField(primary_key=True)
    board = models.ForeignKey(KanbanBoard, on_delete=models.CASCADE, related_name='cards')
    column = models.ForeignKey(KanbanColumn, on_delete=models.CASCADE, related_name='cards')
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='kanban_cards')
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True, related_name='kanban_cards')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=20, blank=True)
    due_date = models.DateField(null=True, blank=True)
    estimate_hours = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    actual_hours = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, default='todo')
    sort_order = models.PositiveIntegerField(default=0)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'kanban_cards'
        ordering = ['sort_order', 'id']


class KanbanCardActivity(models.Model):
    id = models.BigAutoField(primary_key=True)
    card = models.ForeignKey(KanbanCard, on_delete=models.CASCADE, related_name='activities')
    action_type = models.CharField(max_length=50)
    from_value = models.CharField(max_length=255, blank=True)
    to_value = models.CharField(max_length=255, blank=True)
    action_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'kanban_card_activities'


class KanbanLabel(models.Model):
    id = models.BigAutoField(primary_key=True)
    board = models.ForeignKey(KanbanBoard, on_delete=models.CASCADE, related_name='labels')
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'kanban_labels'


class KanbanCardLabel(models.Model):
    id = models.BigAutoField(primary_key=True)
    card = models.ForeignKey(KanbanCard, on_delete=models.CASCADE, related_name='card_labels')
    label = models.ForeignKey(KanbanLabel, on_delete=models.CASCADE, related_name='card_labels')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'kanban_card_labels'
        unique_together = ('card', 'label')
