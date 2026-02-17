from rest_framework.views import APIView
from rest_framework import status
from common.responses import ApiResponse
from core.models.calendar_kanban import CalendarEvent, KanbanBoard, KanbanColumn, KanbanCard
from core.serializers.User.calendar_kanban_serializer import (
    CalendarEventSerializer,
    CalendarEventCreateSerializer,
    CalendarEventUpdateSerializer,
    KanbanBoardSerializer,
    KanbanColumnSerializer,
    KanbanCardSerializer,
)
from core.services.User.calendar_kanban_service import CalendarService, KanbanService


def _error_message(e):
    if hasattr(e, 'detail'):
        detail = e.detail
        if isinstance(detail, list) and detail:
            return str(detail[0])
        return str(detail)
    return str(e)


class CalendarEventListCreateView(APIView):
    def get(self, request):
        events = CalendarService.list_events(
            start_at=request.query_params.get('start_at'),
            end_at=request.query_params.get('end_at'),
            source_type=request.query_params.get('source_type'),
        )
        return ApiResponse.success('Calendar events fetched successfully', CalendarEventSerializer(events, many=True).data)

    def post(self, request):
        serializer = CalendarEventCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event = CalendarService.create_event(serializer.validated_data)
        return ApiResponse.success('Calendar event created successfully', CalendarEventSerializer(event).data, status.HTTP_201_CREATED)


class CalendarEventDetailView(APIView):
    def get_object(self, event_id):
        return CalendarEvent.objects.filter(id=event_id).first()

    def get(self, request, event_id):
        event = self.get_object(event_id)
        if not event:
            return ApiResponse.error('Calendar event not found', status.HTTP_404_NOT_FOUND)
        return ApiResponse.success('Calendar event fetched successfully', CalendarEventSerializer(event).data)

    def patch(self, request, event_id):
        event = self.get_object(event_id)
        if not event:
            return ApiResponse.error('Calendar event not found', status.HTTP_404_NOT_FOUND)
        serializer = CalendarEventUpdateSerializer(event, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        event = CalendarService.update_event(event, serializer.validated_data)
        return ApiResponse.success('Calendar event updated successfully', CalendarEventSerializer(event).data)

    def delete(self, request, event_id):
        event = self.get_object(event_id)
        if not event:
            return ApiResponse.error('Calendar event not found', status.HTTP_404_NOT_FOUND)
        event.delete()
        return ApiResponse.success('Calendar event deleted successfully')


class CalendarTaskFeedView(APIView):
    def get(self, request):
        return ApiResponse.success('Task calendar feed fetched successfully', CalendarService.task_feed())


class CalendarInvoiceFeedView(APIView):
    def get(self, request):
        return ApiResponse.success('Invoice calendar feed fetched successfully', CalendarService.invoice_feed())


class KanbanBoardListCreateView(APIView):
    def get(self, request):
        boards = KanbanService.list_boards()
        return ApiResponse.success('Kanban boards fetched successfully', KanbanBoardSerializer(boards, many=True).data)

    def post(self, request):
        serializer = KanbanBoardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        board = KanbanService.create_board(serializer.validated_data)
        return ApiResponse.success('Kanban board created successfully', KanbanBoardSerializer(board).data, status.HTTP_201_CREATED)


class KanbanBoardDetailView(APIView):
    def get_object(self, board_id):
        return KanbanBoard.objects.filter(id=board_id).first()

    def get(self, request, board_id):
        board = self.get_object(board_id)
        if not board:
            return ApiResponse.error('Kanban board not found', status.HTTP_404_NOT_FOUND)
        payload = KanbanBoardSerializer(board).data
        payload['columns'] = KanbanColumnSerializer(board.columns.all().order_by('sort_order', 'id'), many=True).data
        payload['cards'] = KanbanCardSerializer(board.cards.filter(is_archived=False).order_by('sort_order', 'id'), many=True).data
        return ApiResponse.success('Kanban board fetched successfully', payload)

    def patch(self, request, board_id):
        board = self.get_object(board_id)
        if not board:
            return ApiResponse.error('Kanban board not found', status.HTTP_404_NOT_FOUND)

        serializer = KanbanBoardSerializer(board, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        board = KanbanService.update_board(board, serializer.validated_data)
        return ApiResponse.success('Kanban board updated successfully', KanbanBoardSerializer(board).data)

    def delete(self, request, board_id):
        board = self.get_object(board_id)
        if not board:
            return ApiResponse.error('Kanban board not found', status.HTTP_404_NOT_FOUND)
        KanbanService.delete_board(board)
        return ApiResponse.success('Kanban board deleted successfully')


class KanbanColumnCreateView(APIView):
    def post(self, request, board_id):
        board = KanbanBoard.objects.filter(id=board_id).first()
        if not board:
            return ApiResponse.error('Kanban board not found', status.HTTP_404_NOT_FOUND)

        serializer = KanbanColumnSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        column = KanbanService.create_column(board, serializer.validated_data)
        return ApiResponse.success('Kanban column created successfully', KanbanColumnSerializer(column).data, status.HTTP_201_CREATED)


class KanbanColumnDetailView(APIView):
    def patch(self, request, column_id):
        column = KanbanColumn.objects.filter(id=column_id).first()
        if not column:
            return ApiResponse.error('Kanban column not found', status.HTTP_404_NOT_FOUND)

        serializer = KanbanColumnSerializer(column, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        column = KanbanService.update_column(column, serializer.validated_data)
        return ApiResponse.success('Kanban column updated successfully', KanbanColumnSerializer(column).data)

    def delete(self, request, column_id):
        column = KanbanColumn.objects.filter(id=column_id).first()
        if not column:
            return ApiResponse.error('Kanban column not found', status.HTTP_404_NOT_FOUND)
        KanbanService.delete_column(column)
        return ApiResponse.success('Kanban column deleted successfully')


class KanbanCardCreateView(APIView):
    def post(self, request, column_id):
        column = KanbanColumn.objects.filter(id=column_id).first()
        if not column:
            return ApiResponse.error('Kanban column not found', status.HTTP_404_NOT_FOUND)

        serializer = KanbanCardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        card = KanbanService.create_card(column, serializer.validated_data)
        return ApiResponse.success('Kanban card created successfully', KanbanCardSerializer(card).data, status.HTTP_201_CREATED)


class KanbanCardDetailView(APIView):
    def patch(self, request, card_id):
        card = KanbanCard.objects.filter(id=card_id).first()
        if not card:
            return ApiResponse.error('Kanban card not found', status.HTTP_404_NOT_FOUND)

        serializer = KanbanCardSerializer(card, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        try:
            card = KanbanService.update_card(card, serializer.validated_data)
            return ApiResponse.success('Kanban card updated successfully', KanbanCardSerializer(card).data)
        except Exception as e:
            return ApiResponse.error(_error_message(e), status.HTTP_400_BAD_REQUEST)

    def delete(self, request, card_id):
        card = KanbanCard.objects.filter(id=card_id).first()
        if not card:
            return ApiResponse.error('Kanban card not found', status.HTTP_404_NOT_FOUND)
        KanbanService.delete_card(card)
        return ApiResponse.success('Kanban card deleted successfully')


class KanbanCardMoveView(APIView):
    def post(self, request, card_id):
        card = KanbanCard.objects.filter(id=card_id).first()
        if not card:
            return ApiResponse.error('Kanban card not found', status.HTTP_404_NOT_FOUND)

        target_column_id = request.data.get('column_id')
        sort_order = request.data.get('sort_order')
        try:
            card = KanbanService.move_card(card, target_column_id, sort_order)
            return ApiResponse.success('Kanban card moved successfully', KanbanCardSerializer(card).data)
        except Exception as e:
            return ApiResponse.error(_error_message(e), status.HTTP_400_BAD_REQUEST)
