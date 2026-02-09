from rest_framework import serializers
from core.models.project import Project
from core.models.client import Client


class ProjectSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.name', read_only=True)

    class Meta:
        model = Project
        fields = [
            'id', 'client', 'client_name',
            'name', 'description', 'status', 'priority',
            'billing_type', 'hourly_rate', 'fixed_price', 'currency',
            'estimated_hours', 'progress_percent',
            'start_date', 'due_date',
            'notes', 'metadata',
            'is_active', 'archived_at', 'created_at', 'updated_at'
        ]


class ProjectCreateSerializer(serializers.ModelSerializer):
    client = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all())

    class Meta:
        model = Project
        fields = [
            'client',
            'name', 'description', 'status', 'priority',
            'billing_type', 'hourly_rate', 'fixed_price', 'currency',
            'estimated_hours', 'progress_percent',
            'start_date', 'due_date',
            'notes', 'metadata'
        ]

    def validate_currency(self, value):
        if value and len(value) != 3:
            raise serializers.ValidationError("Currency must be a 3-letter code.")
        return value.upper() if value else value

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

        billing_type = attrs.get('billing_type')
        if billing_type == Project.BILLING_HOURLY and not attrs.get('hourly_rate'):
            raise serializers.ValidationError("Hourly rate is required for hourly billing.")
        if billing_type == Project.BILLING_FIXED and not attrs.get('fixed_price'):
            raise serializers.ValidationError("Fixed price is required for fixed billing.")
        return attrs


class ProjectUpdateSerializer(serializers.ModelSerializer):
    client = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all(), required=False)

    class Meta:
        model = Project
        fields = [
            'client',
            'name', 'description', 'status', 'priority',
            'billing_type', 'hourly_rate', 'fixed_price', 'currency',
            'estimated_hours', 'progress_percent',
            'start_date', 'due_date',
            'notes', 'metadata', 'is_active'
        ]

    def validate_currency(self, value):
        if value and len(value) != 3:
            raise serializers.ValidationError("Currency must be a 3-letter code.")
        return value.upper() if value else value

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

        billing_type = attrs.get('billing_type', self.instance.billing_type if self.instance else None)
        hourly_rate = attrs.get('hourly_rate', self.instance.hourly_rate if self.instance else None)
        fixed_price = attrs.get('fixed_price', self.instance.fixed_price if self.instance else None)

        if billing_type == Project.BILLING_HOURLY and not hourly_rate:
            raise serializers.ValidationError("Hourly rate is required for hourly billing.")
        if billing_type == Project.BILLING_FIXED and not fixed_price:
            raise serializers.ValidationError("Fixed price is required for fixed billing.")
        return attrs
