from rest_framework.views import APIView
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from common.responses import ApiResponse
from core.models.workbench import TimeEntry, TimerSession
from core.serializers.User.workbench_serializer import (
    TimeEntrySerializer,
    TimeEntryCreateSerializer,
    TimeEntryUpdateSerializer,
    TimerSessionSerializer,
    TimerStartSerializer,
    TimerStopSerializer,
    TimerBreakStartSerializer,
    SyncEntriesSerializer,
)
from core.services.User.workbench_service import WorkbenchService


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


def _error_message(e):
    if hasattr(e, 'detail'):
        detail = e.detail
        if isinstance(detail, list) and detail:
            return str(detail[0])
        return str(detail)
    return str(e)


class WorkbenchOverviewView(APIView):
    def get(self, request):
        data = WorkbenchService.get_overview()
        active = data.pop('active_timer')
        data['active_timer'] = TimerSessionSerializer(active).data if active else None
        return ApiResponse.success(message='Workbench overview fetched successfully', data=data)


class WorkbenchProjectsView(APIView):
    def get(self, request):
        data = []
        for row in WorkbenchService.list_projects():
            project = row['project']
            data.append({
                'project_id': str(project.id),
                'name': project.name,
                'status': project.status,
                'tracked_seconds': row['tracked_seconds'],
                'client_id': str(project.client_id),
            })
        return ApiResponse.success(message='Workbench projects fetched successfully', data=data)


class WorkbenchProjectTasksView(APIView):
    def get(self, request, project_id):
        tasks = WorkbenchService.list_project_tasks(project_id)
        payload = [{
            'task_id': str(t.id),
            'title': t.title,
            'status': t.status,
            'progress_percent': t.progress_percent,
            'billable': t.billable,
            'estimated_hours': t.estimated_hours,
            'actual_hours': t.actual_hours,
        } for t in tasks]
        return ApiResponse.success(message='Workbench project tasks fetched successfully', data=payload)


class WorkbenchActiveTimerView(APIView):
    def get(self, request):
        timer = WorkbenchService._active_timer()
        return ApiResponse.success(
            message='Active timer fetched successfully',
            data=TimerSessionSerializer(timer).data if timer else None,
        )


class WorkbenchTimerStartView(APIView):
    def post(self, request):
        serializer = TimerStartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            session = WorkbenchService.start_timer(
                project_id=serializer.validated_data['project_id'],
                task_id=serializer.validated_data['task_id'],
                started_from=serializer.validated_data['started_from'],
                offline_mode=serializer.validated_data['offline_mode'],
                local_session_uuid=serializer.validated_data['local_session_uuid'],
            )
            return ApiResponse.success('Timer started successfully', TimerSessionSerializer(session).data, status.HTTP_201_CREATED)
        except Exception as e:
            return ApiResponse.error(_error_message(e), status.HTTP_400_BAD_REQUEST)


class WorkbenchTimerPauseView(APIView):
    def post(self, request):
        try:
            session = WorkbenchService._active_timer()
            if not session:
                return ApiResponse.error('No active timer found', status.HTTP_404_NOT_FOUND)
            session = WorkbenchService.pause_timer(session)
            return ApiResponse.success('Timer paused successfully', TimerSessionSerializer(session).data)
        except Exception as e:
            return ApiResponse.error(_error_message(e), status.HTTP_400_BAD_REQUEST)


class WorkbenchTimerResumeView(APIView):
    def post(self, request):
        try:
            session = WorkbenchService._active_timer()
            if not session:
                return ApiResponse.error('No active timer found', status.HTTP_404_NOT_FOUND)
            session = WorkbenchService.resume_timer(session)
            return ApiResponse.success('Timer resumed successfully', TimerSessionSerializer(session).data)
        except Exception as e:
            return ApiResponse.error(_error_message(e), status.HTTP_400_BAD_REQUEST)


class WorkbenchTimerBreakStartView(APIView):
    def post(self, request):
        serializer = TimerBreakStartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            session = WorkbenchService._active_timer()
            if not session:
                return ApiResponse.error('No active timer found', status.HTTP_404_NOT_FOUND)
            session = WorkbenchService.start_break(session, serializer.validated_data['reason'])
            return ApiResponse.success('Break started successfully', TimerSessionSerializer(session).data)
        except Exception as e:
            return ApiResponse.error(_error_message(e), status.HTTP_400_BAD_REQUEST)


class WorkbenchTimerBreakStopView(APIView):
    def post(self, request):
        try:
            session = WorkbenchService._active_timer()
            if not session:
                return ApiResponse.error('No active timer found', status.HTTP_404_NOT_FOUND)
            session = WorkbenchService.stop_break(session)
            return ApiResponse.success('Break stopped successfully', TimerSessionSerializer(session).data)
        except Exception as e:
            return ApiResponse.error(_error_message(e), status.HTTP_400_BAD_REQUEST)


class WorkbenchTimerStopView(APIView):
    def post(self, request):
        serializer = TimerStopSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            session = WorkbenchService._active_timer()
            if not session:
                return ApiResponse.error('No active timer found', status.HTTP_404_NOT_FOUND)
            session = WorkbenchService.stop_timer(session, note=serializer.validated_data['note'])
            return ApiResponse.success('Timer stopped successfully', TimerSessionSerializer(session).data)
        except Exception as e:
            return ApiResponse.error(_error_message(e), status.HTTP_400_BAD_REQUEST)


class WorkbenchManualEntryView(APIView):
    def post(self, request):
        serializer = TimeEntryCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            entry = WorkbenchService.create_manual_entry(serializer.validated_data)
            return ApiResponse.success('Manual time entry created successfully', TimeEntrySerializer(entry).data, status.HTTP_201_CREATED)
        except Exception as e:
            return ApiResponse.error(_error_message(e), status.HTTP_400_BAD_REQUEST)


class WorkbenchTimeEntryListView(APIView):
    def get(self, request):
        entries = WorkbenchService.list_time_entries(request.query_params)
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(entries, request)
        serializer = TimeEntrySerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class WorkbenchTimeEntryDetailView(APIView):
    def patch(self, request, entry_id):
        entry = TimeEntry.objects.filter(id=entry_id).first()
        if not entry:
            return ApiResponse.error('Time entry not found', status.HTTP_404_NOT_FOUND)

        serializer = TimeEntryUpdateSerializer(entry, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        try:
            entry = WorkbenchService.update_time_entry(entry, serializer.validated_data)
            return ApiResponse.success('Time entry updated successfully', TimeEntrySerializer(entry).data)
        except Exception as e:
            return ApiResponse.error(_error_message(e), status.HTTP_400_BAD_REQUEST)

    def delete(self, request, entry_id):
        entry = TimeEntry.objects.filter(id=entry_id).first()
        if not entry:
            return ApiResponse.error('Time entry not found', status.HTTP_404_NOT_FOUND)
        WorkbenchService.delete_time_entry(entry)
        return ApiResponse.success('Time entry deleted successfully')


class WorkbenchSyncView(APIView):
    def post(self, request):
        serializer = SyncEntriesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            batch, created = WorkbenchService.sync_entries(
                batch_uuid=serializer.validated_data['batch_uuid'],
                entries=serializer.validated_data['entries'],
            )
            return ApiResponse.success(
                'Time entries synced successfully',
                {
                    'batch_id': batch.id,
                    'item_count': len(created),
                    'entries': TimeEntrySerializer(created, many=True).data,
                },
                status.HTTP_201_CREATED,
            )
        except Exception as e:
            return ApiResponse.error(_error_message(e), status.HTTP_400_BAD_REQUEST)
