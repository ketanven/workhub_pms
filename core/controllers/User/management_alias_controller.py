from rest_framework.views import APIView
from rest_framework import status
from common.responses import ApiResponse
from core.serializers.User.task_serializer import TaskSerializer, TaskCreateSerializer
from core.services.User.task_service import TaskService


class ProjectTaskListCreateAliasView(APIView):
    def get(self, request, project_id):
        tasks = TaskService.list_tasks(
            request.user,
            project_id=project_id,
            active=request.query_params.get('active'),
            status=request.query_params.get('status'),
            priority=request.query_params.get('priority'),
            search=request.query_params.get('search'),
        )
        return ApiResponse.success('Project tasks fetched successfully', TaskSerializer(tasks, many=True).data)

    def post(self, request, project_id):
        payload = request.data.copy()
        payload['project'] = project_id

        serializer = TaskCreateSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        try:
            task = TaskService.create_task(request.user, serializer.validated_data)
            return ApiResponse.success('Task created successfully', TaskSerializer(task).data, status.HTTP_201_CREATED)
        except Exception as e:
            message = str(e)
            if hasattr(e, 'detail'):
                detail = e.detail
                if isinstance(detail, list) and detail:
                    message = str(detail[0])
                else:
                    message = str(detail)
            return ApiResponse.error(message=message, status=status.HTTP_400_BAD_REQUEST)
