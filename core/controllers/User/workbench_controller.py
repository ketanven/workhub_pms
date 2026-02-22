from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.services.workbench.timer_service import get_active_timer , start_timer , stop_timer , pause_timer , resume_timer , start_break , stop_break , create_manual_time_entry , get_time_entries , update_time_entry , delete_time_entry , get_workbench_projects , get_project_tasks , get_workbench_overview , sync_time_entries



class StartTimerView(APIView):

    def post(self, request):
        project_id = request.data.get("project_id")
        task_id = request.data.get("task_id")

        if not project_id or not task_id:
            return Response(
                {"error": "project_id and task_id are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        session = start_timer(project_id, task_id)

        return Response(
            {
                "message": "Timer started successfully",
                "session_id": session.id,
                "status": session.status,
                "started_at": session.started_at
            },
            status=status.HTTP_201_CREATED
        )
    


class ActiveTimerView(APIView):

    def get(self, request):
        session = get_active_timer()

        if not session:
            return Response(
                {"message": "No active timer"},
                status=status.HTTP_200_OK
            )

        return Response(
            {
                "session_id": session.id,
                "project_id": session.project_id,
                "task_id": session.task_id,
                "started_at": session.started_at,
                "status": session.status
            },
            status=status.HTTP_200_OK
        )
    



class StopTimerView(APIView):

    def post(self, request):
        session = stop_timer()

        if not session:
            return Response(
                {"error": "No active timer to stop"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                "message": "Timer stopped successfully",
                "session_id": session.id,
                "duration_seconds": session.total_elapsed_seconds,
                "status": session.status
            },
            status=status.HTTP_200_OK
        )
    

class PauseTimerView(APIView):

    def post(self, request):
        session = pause_timer()

        if not session:
            return Response(
                {"error": "No running timer to pause"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                "message": "Timer paused successfully",
                "session_id": session.id,
                "status": session.status
            },
            status=status.HTTP_200_OK
        )
    


class ResumeTimerView(APIView):

    def post(self, request):
        session = resume_timer()

        if not session:
            return Response(
                {"error": "No paused timer to resume"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                "message": "Timer resumed successfully",
                "session_id": session.id,
                "status": session.status,
                "total_break_seconds": session.total_break_seconds
            },
            status=status.HTTP_200_OK
        )
    



class StartBreakView(APIView):

    def post(self, request):
        session, error = start_break()

        if error:
            return Response(
                {"error": error},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                "message": "Break started successfully",
                "session_id": session.id
            },
            status=status.HTTP_200_OK
        )
    


class StopBreakView(APIView):

    def post(self, request):
        session, error = stop_break()

        if error:
            return Response(
                {"error": error},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                "message": "Break stopped successfully",
                "session_id": session.id,
                "total_break_seconds": session.total_break_seconds
            },
            status=status.HTTP_200_OK
        )
    


class ManualTimeEntryView(APIView):

    def post(self, request):
        time_entry, error = create_manual_time_entry(request.data)

        if error:
            return Response(
                {"error": error},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                "message": "Manual time entry created successfully",
                "entry_id": time_entry.id,
                "duration_seconds": time_entry.duration_seconds
            },
            status=status.HTTP_201_CREATED
        )
    


class TimeEntriesListView(APIView):

    def get(self, request):
        filters = {
            "entry_date": request.query_params.get("entry_date"),
            "project_id": request.query_params.get("project_id"),
            "task_id": request.query_params.get("task_id"),
        }

        entries = get_time_entries(filters)

        data = []
        for entry in entries:
            data.append({
                "id": entry.id,
                "project_id": entry.project_id,
                "task_id": entry.task_id,
                "entry_date": entry.entry_date,
                "start_time": entry.start_time,
                "end_time": entry.end_time,
                "duration_seconds": entry.duration_seconds,
                "is_manual": entry.is_manual,
                "is_billable": entry.is_billable,
                "note": entry.note
            })

        return Response(data, status=status.HTTP_200_OK)
    



class UpdateTimeEntryView(APIView):

    def patch(self, request, entry_id):
        entry, error = update_time_entry(entry_id, request.data)

        if error:
            return Response(
                {"error": error},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                "message": "Time entry updated successfully",
                "entry_id": entry.id,
                "duration_seconds": entry.duration_seconds,
                "start_time": entry.start_time,
                "end_time": entry.end_time,
                "is_billable": entry.is_billable,
                "note": entry.note
            },
            status=status.HTTP_200_OK
        )
    


class DeleteTimeEntryView(APIView):

    def delete(self, request, entry_id):
        success, error = delete_time_entry(entry_id)

        if error:
            return Response(
                {"error": error},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {"message": "Time entry deleted successfully"},
            status=status.HTTP_200_OK
        )
    

class WorkbenchProjectListView(APIView):

    def get(self, request):
        projects = get_workbench_projects()

        data = []
        for project in projects:
            data.append({
                "project_id": project.id,
                "project_name": project.name,
                "status": project.status,
                "start_date": project.start_date,
                "end_date": project.due_date
            })

        return Response(data, status=status.HTTP_200_OK)
    


class WorkbenchProjectTasksView(APIView):

    def get(self, request, project_id):
        tasks = get_project_tasks(project_id)

        data = []
        for task in tasks:
            data.append({
                "task_id": task.id,
                "task_name": task.title,   # changed here
                "status": task.status,
                "priority": task.priority,
                "estimated_hours": task.estimated_hours
            })

        return Response(data, status=status.HTTP_200_OK)
    


class WorkbenchOverviewView(APIView):

    def get(self, request):
        data = get_workbench_overview()

        return Response(data, status=status.HTTP_200_OK)
    

class SyncTimeEntriesView(APIView):

    def post(self, request):
        result, error = sync_time_entries(request.data)

        if error:
            return Response(
                {"error": error},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(result, status=status.HTTP_200_OK)