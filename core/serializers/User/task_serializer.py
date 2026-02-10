from rest_framework import serializers
from core.models.task import Task
from core.models.project import Project


class TaskSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'project', 'project_name',
            'title', 'description', 'status', 'priority',
            'estimated_hours', 'actual_hours', 'progress_percent',
            'start_date', 'due_date', 'completed_at',
            'billable', 'hourly_rate',
            'notes', 'metadata',
            'is_active', 'archived_at', 'created_at', 'updated_at'
        ]


class TaskCreateSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())

    class Meta:
        model = Task
        fields = [
            'project',
            'title', 'description', 'status', 'priority',
            'estimated_hours', 'actual_hours', 'progress_percent',
            'start_date', 'due_date', 'completed_at',
            'billable', 'hourly_rate',
            'notes', 'metadata'
        ]

    def validate_progress_percent(self, value):
        if value is None:
            return value
        if value < 0 or value > 100:
            raise serializers.ValidationError("Progress percent must be between 0 and 100.")
        return value

    def validate(self, attrs):
        start_date = attrs.get('start_date')
        due_date = attrs.get('due_date')
        if start_date and due_date and due_date < start_date:
            raise serializers.ValidationError("Due date cannot be before start date.")

        if attrs.get('billable') and attrs.get('hourly_rate') is None:
            raise serializers.ValidationError("Hourly rate is required for billable tasks.")
        return attrs


class TaskUpdateSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all(), required=False)

    class Meta:
        model = Task
        fields = [
            'project',
            'title', 'description', 'status', 'priority',
            'estimated_hours', 'actual_hours', 'progress_percent',
            'start_date', 'due_date', 'completed_at',
            'billable', 'hourly_rate',
            'notes', 'metadata', 'is_active'
        ]

    def validate_progress_percent(self, value):
        if value is None:
            return value
        if value < 0 or value > 100:
            raise serializers.ValidationError("Progress percent must be between 0 and 100.")
        return value

    def validate(self, attrs):
        start_date = attrs.get('start_date', self.instance.start_date if self.instance else None)
        due_date = attrs.get('due_date', self.instance.due_date if self.instance else None)
        if start_date and due_date and due_date < start_date:
            raise serializers.ValidationError("Due date cannot be before start date.")

        billable = attrs.get('billable', self.instance.billable if self.instance else True)
        hourly_rate = attrs.get('hourly_rate', self.instance.hourly_rate if self.instance else None)
        if billable and hourly_rate is None:
            raise serializers.ValidationError("Hourly rate is required for billable tasks.")
        return attrs
