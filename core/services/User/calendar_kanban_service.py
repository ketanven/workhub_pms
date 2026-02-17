from django.utils import timezone
from rest_framework.exceptions import ValidationError
from core.models.calendar_kanban import (
    CalendarEvent,
    KanbanBoard,
    KanbanColumn,
    KanbanCard,
    KanbanCardActivity,
)
from core.models.task import Task
from core.models.invoicing import Invoice


class CalendarService:
    @staticmethod
    def list_events(start_at=None, end_at=None, source_type=None):
        queryset = CalendarEvent.objects.all().order_by('start_at')
        if start_at:
            queryset = queryset.filter(start_at__gte=start_at)
        if end_at:
            queryset = queryset.filter(end_at__lte=end_at)
        if source_type:
            queryset = queryset.filter(source_type=source_type)
        return queryset

    @staticmethod
    def create_event(data):
        return CalendarEvent.objects.create(**data)

    @staticmethod
    def update_event(event, data):
        for key, value in data.items():
            setattr(event, key, value)
        event.save()
        return event

    @staticmethod
    def task_feed():
        tasks = Task.objects.filter(due_date__isnull=False, is_active=True).order_by('due_date')
        data = []
        for task in tasks:
            start = timezone.datetime.combine(task.due_date, timezone.datetime.min.time(), tzinfo=timezone.get_current_timezone())
            data.append({
                'source': 'task',
                'source_id': str(task.id),
                'title': task.title,
                'start_at': start,
                'end_at': start,
                'status': task.status,
            })
        return data

    @staticmethod
    def invoice_feed():
        invoices = Invoice.objects.filter(due_date__isnull=False).order_by('due_date')
        data = []
        for invoice in invoices:
            start = timezone.datetime.combine(invoice.due_date, timezone.datetime.min.time(), tzinfo=timezone.get_current_timezone())
            data.append({
                'source': 'invoice',
                'source_id': invoice.id,
                'title': f'Invoice {invoice.invoice_number} due',
                'start_at': start,
                'end_at': start,
                'status': invoice.status,
            })
        return data


class KanbanService:
    @staticmethod
    def list_boards():
        return KanbanBoard.objects.filter(is_archived=False).order_by('sort_order', 'id')

    @staticmethod
    def create_board(data):
        board = KanbanBoard.objects.create(**data)
        KanbanColumn.objects.create(board=board, name='To Do', sort_order=1)
        KanbanColumn.objects.create(board=board, name='In Progress', sort_order=2)
        KanbanColumn.objects.create(board=board, name='Done', sort_order=3, is_done_column=True)
        return board

    @staticmethod
    def update_board(board, data):
        for key, value in data.items():
            setattr(board, key, value)
        board.save()
        return board

    @staticmethod
    def delete_board(board):
        board.is_archived = True
        board.save()
        return board

    @staticmethod
    def create_column(board, data):
        return KanbanColumn.objects.create(board=board, **data)

    @staticmethod
    def update_column(column, data):
        for key, value in data.items():
            setattr(column, key, value)
        column.save()
        return column

    @staticmethod
    def delete_column(column):
        column.delete()

    @staticmethod
    def create_card(column, data):
        data['board'] = column.board
        data['column'] = column
        return KanbanCard.objects.create(**data)

    @staticmethod
    def update_card(card, data):
        for key, value in data.items():
            setattr(card, key, value)
        card.save()
        return card

    @staticmethod
    def move_card(card, target_column_id, sort_order=None):
        target = KanbanColumn.objects.filter(id=target_column_id).first()
        if not target:
            raise ValidationError('Target column not found')
        old_column_id = card.column_id
        card.column = target
        if sort_order is not None:
            card.sort_order = sort_order
        card.save()
        KanbanCardActivity.objects.create(
            card=card,
            action_type='move',
            from_value=str(old_column_id),
            to_value=str(target.id),
            action_note='Card moved between columns',
        )
        return card

    @staticmethod
    def delete_card(card):
        card.is_archived = True
        card.save()
        return card
