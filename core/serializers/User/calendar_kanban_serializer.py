from rest_framework import serializers
from core.models.calendar_kanban import (
    CalendarEvent,
    KanbanBoard,
    KanbanColumn,
    KanbanCard,
)


class CalendarEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalendarEvent
        fields = '__all__'


class CalendarEventCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalendarEvent
        fields = [
            'title', 'description', 'event_type', 'start_at', 'end_at', 'all_day',
            'timezone', 'location', 'color', 'source_type', 'source_id',
            'reminder_minutes_before', 'recurrence_rule', 'status'
        ]


class CalendarEventUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalendarEvent
        fields = [
            'title', 'description', 'event_type', 'start_at', 'end_at', 'all_day',
            'timezone', 'location', 'color', 'source_type', 'source_id',
            'reminder_minutes_before', 'recurrence_rule', 'status'
        ]


class KanbanBoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = KanbanBoard
        fields = '__all__'


class KanbanColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = KanbanColumn
        fields = '__all__'


class KanbanCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = KanbanCard
        fields = '__all__'
