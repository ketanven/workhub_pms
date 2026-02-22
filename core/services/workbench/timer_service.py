from django.utils import timezone
from core.models.workbench import TimerSession


def start_timer(project_id, task_id):
    # Check if any timer is already running
    active_session = TimerSession.objects.filter(status="running").first()

    if active_session:
        active_session.status = "stopped"
        active_session.stopped_at = timezone.now()
        active_session.save()

    # Create new timer session
    new_session = TimerSession.objects.create(
        project_id=project_id,
        task_id=task_id,
        started_at=timezone.now(),
        status="running"
    )

    return new_session


def get_active_timer():
    return TimerSession.objects.filter(status="running").first()


def stop_timer():
    from django.utils import timezone
    from core.models.workbench import TimerSession, TimeEntry

    session = TimerSession.objects.filter(status="running").first()

    if not session:
        return None

    session.stopped_at = timezone.now()
    session.status = "stopped"

    # Calculate total duration
    total_duration = (session.stopped_at - session.started_at).total_seconds()

    # Subtract break time
    net_duration = int(total_duration - session.total_break_seconds)

    if net_duration < 0:
        net_duration = 0

    session.total_elapsed_seconds = net_duration
    session.save()

    # Create TimeEntry automatically
    TimeEntry.objects.create(
        project_id=session.project_id,
        task_id=session.task_id,
        entry_date=session.started_at.date(),
        start_time=session.started_at.time(),
        end_time=session.stopped_at.time(),
        duration_seconds=net_duration,
        is_manual=False,
        source="timer",
        is_billable=True
    )

    return session



def pause_timer():
    from django.utils import timezone

    session = TimerSession.objects.filter(status="running").first()

    if not session:
        return None

    session.paused_at = timezone.now()
    session.status = "paused"
    session.save()

    return session


def resume_timer():
    from django.utils import timezone

    session = TimerSession.objects.filter(status="paused").first()

    if not session:
        return None

    now = timezone.now()

    # Calculate break duration
    break_duration = (now - session.paused_at).total_seconds()
    session.total_break_seconds += int(break_duration)

    session.resumed_at = now
    session.status = "running"

    session.save()

    return session






def start_break():
    from django.utils import timezone
    from core.models.workbench import TimerSession, TimerBreak

    session = TimerSession.objects.filter(status="running").first()

    if not session:
        return None, "No running session"

    # Check if there is already an active break
    active_break = TimerBreak.objects.filter(
        timer_session=session,
        break_ended_at__isnull=True
    ).first()

    if active_break:
        return None, "Break already started"

    TimerBreak.objects.create(
        timer_session=session,
        break_started_at=timezone.now()
    )

    return session, None


def stop_break():
    from django.utils import timezone
    from core.models.workbench import TimerSession, TimerBreak

    session = TimerSession.objects.filter(status="running").first()

    if not session:
        return None, "No running session"

    active_break = TimerBreak.objects.filter(
        timer_session=session,
        break_ended_at__isnull=True
    ).first()

    if not active_break:
        return None, "No active break found"

    now = timezone.now()
    break_duration = int((now - active_break.break_started_at).total_seconds())

    active_break.break_ended_at = now
    active_break.break_duration_seconds = break_duration
    active_break.save()

    session.total_break_seconds += break_duration
    session.save()

    return session, None



def create_manual_time_entry(data):
    from datetime import datetime
    from core.models.workbench import TimeEntry
    from core.models.project import Project
    from core.models.task import Task

    project_id = data.get("project_id")
    task_id = data.get("task_id")
    entry_date = data.get("entry_date")
    start_time = data.get("start_time")
    end_time = data.get("end_time")
    note = data.get("note", "")
    is_billable = data.get("is_billable", True)

    if not all([project_id, task_id, entry_date, start_time, end_time]):
        return None, "All required fields must be provided"

    try:
        start_dt = datetime.strptime(start_time, "%H:%M:%S")
        end_dt = datetime.strptime(end_time, "%H:%M:%S")
    except ValueError:
        return None, "Invalid time format. Use HH:MM:SS"

    if end_dt <= start_dt:
        return None, "end_time must be greater than start_time"

    duration_seconds = int((end_dt - start_dt).total_seconds())

    time_entry = TimeEntry.objects.create(
        project_id=project_id,
        task_id=task_id,
        entry_date=entry_date,
        start_time=start_time,
        end_time=end_time,
        duration_seconds=duration_seconds,
        is_manual=True,
        source="manual",
        note=note,
        is_billable=is_billable
    )

    return time_entry, None



def get_time_entries(filters=None):
    from core.models.workbench import TimeEntry

    queryset = TimeEntry.objects.all().order_by("-created_at")

    if filters:
        entry_date = filters.get("entry_date")
        project_id = filters.get("project_id")
        task_id = filters.get("task_id")

        if entry_date:
            queryset = queryset.filter(entry_date=entry_date)

        if project_id:
            queryset = queryset.filter(project_id=project_id)

        if task_id:
            queryset = queryset.filter(task_id=task_id)

    return queryset





def update_time_entry(entry_id, data):
    from datetime import datetime
    from core.models.workbench import TimeEntry

    try:
        entry = TimeEntry.objects.get(id=entry_id)
    except TimeEntry.DoesNotExist:
        return None, "Time entry not found"

    start_time = data.get("start_time")
    end_time = data.get("end_time")
    note = data.get("note")
    is_billable = data.get("is_billable")

    # Update start/end time if provided
    if start_time:
        try:
            entry.start_time = datetime.strptime(start_time, "%H:%M:%S").time()
        except ValueError:
            return None, "Invalid start_time format. Use HH:MM:SS"

    if end_time:
        try:
            entry.end_time = datetime.strptime(end_time, "%H:%M:%S").time()
        except ValueError:
            return None, "Invalid end_time format. Use HH:MM:SS"

    # Recalculate duration if both exist
    if entry.start_time and entry.end_time:
        start_dt = datetime.combine(datetime.today(), entry.start_time)
        end_dt = datetime.combine(datetime.today(), entry.end_time)

        if end_dt <= start_dt:
            return None, "end_time must be greater than start_time"

        entry.duration_seconds = int((end_dt - start_dt).total_seconds())

    # Update optional fields
    if note is not None:
        entry.note = note

    if is_billable is not None:
        entry.is_billable = is_billable

    entry.save()

    return entry, None





def delete_time_entry(entry_id):
    from core.models.workbench import TimeEntry

    try:
        entry = TimeEntry.objects.get(id=entry_id)
    except TimeEntry.DoesNotExist:
        return None, "Time entry not found"

    entry.delete()

    return True, None



def get_workbench_projects():
    from core.models.project import Project

    return Project.objects.all().order_by("-created_at")



def get_project_tasks(project_id):
    from core.models.task import Task

    return Task.objects.filter(project_id=project_id).order_by("-created_at")



def get_workbench_overview():
    from datetime import date, timedelta
    from django.utils import timezone
    from core.models.workbench import TimeEntry, TimerSession

    today = date.today()

    # Today entries
    today_entries = TimeEntry.objects.filter(entry_date=today)
    today_seconds = sum(e.duration_seconds for e in today_entries)

    # Week calculation (Monday start)
    start_of_week = today - timedelta(days=today.weekday())
    week_entries = TimeEntry.objects.filter(entry_date__gte=start_of_week)
    week_seconds = sum(e.duration_seconds for e in week_entries)

    # Month calculation
    start_of_month = today.replace(day=1)
    month_entries = TimeEntry.objects.filter(entry_date__gte=start_of_month)
    month_seconds = sum(e.duration_seconds for e in month_entries)

    # Billable hours (month)
    billable_entries = month_entries.filter(is_billable=True)
    billable_seconds = sum(e.duration_seconds for e in billable_entries)

    # Active timer
    active_session = TimerSession.objects.filter(status="running").first()

    return {
        "today_seconds": today_seconds,
        "week_seconds": week_seconds,
        "month_seconds": month_seconds,
        "billable_seconds_month": billable_seconds,
        "active_timer": {
            "session_id": active_session.id,
            "task_id": active_session.task_id,
            "project_id": active_session.project_id,
            "started_at": active_session.started_at
        } if active_session else None
    }




def sync_time_entries(data):
    from django.utils import timezone
    from core.models.workbench import TimeEntry, OfflineSyncBatch
    from datetime import datetime

    batch_uuid = data.get("batch_uuid")
    entries = data.get("entries")

    if not batch_uuid or not entries:
        return None, "batch_uuid and entries are required"

    # Create sync batch record
    batch = OfflineSyncBatch.objects.create(
        batch_uuid=batch_uuid,
        payload_json=data,
        item_count=len(entries),
        sync_status="processing",
        attempted_at=timezone.now()
    )

    created_count = 0
    skipped_duplicates = 0

    try:
        for entry in entries:

            local_uuid = entry.get("local_entry_uuid")

            # Duplicate protection
            if local_uuid and TimeEntry.objects.filter(local_entry_uuid=local_uuid).exists():
                skipped_duplicates += 1
                continue

            # Parse time fields
            start_time = datetime.strptime(entry.get("start_time"), "%H:%M:%S").time()
            end_time = datetime.strptime(entry.get("end_time"), "%H:%M:%S").time()

            TimeEntry.objects.create(
                project_id=entry.get("project_id"),
                task_id=entry.get("task_id"),
                entry_date=entry.get("entry_date"),
                start_time=start_time,
                end_time=end_time,
                duration_seconds=entry.get("duration_seconds"),
                is_manual=entry.get("is_manual", False),
                is_billable=entry.get("is_billable", True),
                note=entry.get("note"),
                local_entry_uuid=local_uuid,
                source="sync"
            )

            created_count += 1

        batch.sync_status = "completed"
        batch.completed_at = timezone.now()
        batch.save()

        return {
            "batch_uuid": batch_uuid,
            "total_received": len(entries),
            "created": created_count,
            "skipped_duplicates": skipped_duplicates,
            "status": "completed"
        }, None

    except Exception as e:
        batch.sync_status = "failed"
        batch.error_message = str(e)
        batch.save()

        return None, str(e)