from datetime import timedelta
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from core.models.project import Project
from core.models.task import Task
from core.models.workbench import TimeEntry, TimerSession, TimerBreak, OfflineSyncBatch


class WorkbenchService:
    @staticmethod
    def _active_timer():
        return TimerSession.objects.filter(status__in=['running', 'paused', 'break']).order_by('-started_at').first()

    @staticmethod
    def get_overview():
        now = timezone.now()
        today = now.date()
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)

        today_seconds = TimeEntry.objects.filter(entry_date=today).aggregate(total=Sum('duration_seconds'))['total'] or 0
        week_seconds = TimeEntry.objects.filter(entry_date__gte=week_start, entry_date__lte=today).aggregate(total=Sum('duration_seconds'))['total'] or 0
        month_seconds = TimeEntry.objects.filter(entry_date__gte=month_start, entry_date__lte=today).aggregate(total=Sum('duration_seconds'))['total'] or 0

        earnings = TimeEntry.objects.filter(entry_date__gte=month_start, entry_date__lte=today).aggregate(total=Sum('amount_snapshot'))['total'] or 0
        billable_seconds = TimeEntry.objects.filter(entry_date__gte=month_start, entry_date__lte=today, is_billable=True).aggregate(total=Sum('duration_seconds'))['total'] or 0
        utilization = round((billable_seconds / month_seconds) * 100, 2) if month_seconds else 0

        return {
            'active_timer': WorkbenchService._active_timer(),
            'today_seconds': today_seconds,
            'week_seconds': week_seconds,
            'month_seconds': month_seconds,
            'earnings': earnings,
            'utilization_percent': utilization,
        }

    @staticmethod
    def list_projects():
        projects = Project.objects.filter(is_active=True).order_by('-created_at')
        project_data = []
        for project in projects:
            seconds = TimeEntry.objects.filter(project=project).aggregate(total=Sum('duration_seconds'))['total'] or 0
            project_data.append({'project': project, 'tracked_seconds': seconds})
        return project_data

    @staticmethod
    def list_project_tasks(project_id):
        return Task.objects.filter(project_id=project_id, is_active=True).order_by('-created_at')

    @staticmethod
    @transaction.atomic
    def start_timer(project_id, task_id, started_from='web', offline_mode=False, local_session_uuid=''):
        project = Project.objects.filter(id=project_id, is_active=True).first()
        task = Task.objects.filter(id=task_id, is_active=True).first()
        if not project or not task:
            raise ValidationError('Project or task not found.')

        active = WorkbenchService._active_timer()
        if active:
            WorkbenchService.stop_timer(active, note='Auto-stopped due to new timer start')

        return TimerSession.objects.create(
            project=project,
            task=task,
            started_at=timezone.now(),
            status=TimerSession.STATUS_RUNNING,
            started_from=started_from,
            offline_mode=offline_mode,
            local_session_uuid=local_session_uuid,
        )

    @staticmethod
    def pause_timer(session):
        if session.status != TimerSession.STATUS_RUNNING:
            raise ValidationError('Only running timers can be paused.')
        now = timezone.now()
        session.paused_at = now
        session.status = TimerSession.STATUS_PAUSED
        session.total_elapsed_seconds += int((now - (session.resumed_at or session.started_at)).total_seconds())
        session.save()
        return session

    @staticmethod
    def resume_timer(session):
        if session.status not in [TimerSession.STATUS_PAUSED, TimerSession.STATUS_BREAK]:
            raise ValidationError('Only paused or break timers can be resumed.')
        session.resumed_at = timezone.now()
        session.paused_at = None
        session.status = TimerSession.STATUS_RUNNING
        session.save()
        return session

    @staticmethod
    def start_break(session, reason=''):
        if session.status != TimerSession.STATUS_RUNNING:
            raise ValidationError('Break can start only when timer is running.')
        now = timezone.now()
        session.total_elapsed_seconds += int((now - (session.resumed_at or session.started_at)).total_seconds())
        session.paused_at = now
        session.status = TimerSession.STATUS_BREAK
        session.save()
        TimerBreak.objects.create(timer_session=session, break_started_at=now, reason=reason)
        return session

    @staticmethod
    def stop_break(session):
        if session.status != TimerSession.STATUS_BREAK:
            raise ValidationError('No active break found.')
        open_break = session.breaks.filter(break_ended_at__isnull=True).order_by('-break_started_at').first()
        if not open_break:
            raise ValidationError('No open break found.')
        now = timezone.now()
        open_break.break_ended_at = now
        open_break.break_duration_seconds = int((now - open_break.break_started_at).total_seconds())
        open_break.save()
        session.total_break_seconds += open_break.break_duration_seconds
        session.resumed_at = now
        session.paused_at = None
        session.status = TimerSession.STATUS_RUNNING
        session.save()
        return session

    @staticmethod
    @transaction.atomic
    def stop_timer(session, note=''):
        now = timezone.now()
        if session.status == TimerSession.STATUS_RUNNING:
            session.total_elapsed_seconds += int((now - (session.resumed_at or session.started_at)).total_seconds())
        elif session.status == TimerSession.STATUS_BREAK:
            WorkbenchService.stop_break(session)
            session = TimerSession.objects.get(id=session.id)
            session.total_elapsed_seconds += int((now - (session.resumed_at or session.started_at)).total_seconds())

        session.stopped_at = now
        session.status = TimerSession.STATUS_STOPPED
        session.save()

        task = session.task
        rate = task.hourly_rate or session.project.hourly_rate or 0
        amount = round((session.total_elapsed_seconds / 3600) * float(rate), 2) if rate else 0

        TimeEntry.objects.create(
            project=session.project,
            task=task,
            entry_date=now.date(),
            start_time=session.started_at,
            end_time=now,
            duration_seconds=session.total_elapsed_seconds,
            is_manual=False,
            source='timer',
            note=note,
            is_billable=task.billable,
            hourly_rate_snapshot=rate,
            amount_snapshot=amount,
            sync_status='synced',
            synced_at=now,
        )
        return session

    @staticmethod
    def create_manual_entry(data):
        return TimeEntry.objects.create(**data)

    @staticmethod
    def list_time_entries(filters):
        queryset = TimeEntry.objects.all().order_by('-entry_date', '-created_at')
        date_from = filters.get('date_from')
        date_to = filters.get('date_to')
        project_id = filters.get('project_id')
        task_id = filters.get('task_id')

        if date_from:
            queryset = queryset.filter(entry_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(entry_date__lte=date_to)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        if task_id:
            queryset = queryset.filter(task_id=task_id)

        return queryset

    @staticmethod
    def update_time_entry(entry, data):
        for key, value in data.items():
            setattr(entry, key, value)
        entry.save()
        return entry

    @staticmethod
    def delete_time_entry(entry):
        entry.delete()

    @staticmethod
    @transaction.atomic
    def sync_entries(batch_uuid, entries):
        batch = OfflineSyncBatch.objects.create(
            batch_uuid=batch_uuid,
            payload_json={'entries': entries},
            item_count=len(entries),
            sync_status='processing',
            attempted_at=timezone.now(),
        )

        created_entries = []
        for raw in entries:
            created_entries.append(TimeEntry.objects.create(**raw))

        batch.sync_status = 'completed'
        batch.completed_at = timezone.now()
        batch.save()
        return batch, created_entries
