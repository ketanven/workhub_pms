from rest_framework import serializers
from core.models.workbench import TimeEntry, TimerSession, TimerBreak, OfflineSyncBatch
from core.models.project import Project
from core.models.task import Task


class TimeEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeEntry
        fields = '__all__'


class TimeEntryCreateSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    task = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all())

    class Meta:
        model = TimeEntry
        fields = [
            'project', 'task', 'entry_date', 'start_time', 'end_time', 'duration_seconds',
            'is_manual', 'source', 'note', 'is_billable', 'hourly_rate_snapshot',
            'amount_snapshot', 'local_entry_uuid', 'sync_status'
        ]


class TimeEntryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeEntry
        fields = [
            'entry_date', 'start_time', 'end_time', 'duration_seconds', 'note',
            'is_billable', 'hourly_rate_snapshot', 'amount_snapshot', 'sync_status'
        ]


class TimerSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimerSession
        fields = '__all__'


class TimerStartSerializer(serializers.Serializer):
    project_id = serializers.UUIDField()
    task_id = serializers.UUIDField()
    started_from = serializers.CharField(required=False, default='web')
    offline_mode = serializers.BooleanField(required=False, default=False)
    local_session_uuid = serializers.CharField(required=False, allow_blank=True, default='')


class TimerStopSerializer(serializers.Serializer):
    note = serializers.CharField(required=False, allow_blank=True, default='')


class TimerBreakStartSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True, default='')


class SyncBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfflineSyncBatch
        fields = '__all__'


class SyncEntriesSerializer(serializers.Serializer):
    batch_uuid = serializers.CharField()
    entries = TimeEntryCreateSerializer(many=True)
