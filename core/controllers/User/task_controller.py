from rest_framework.views import APIView
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from common.responses import ApiResponse
from core.models.task import Task
from core.serializers.User.task_serializer import (
    TaskSerializer,
    TaskCreateSerializer,
    TaskUpdateSerializer
)
from core.services.User.task_service import TaskService


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class UserTaskListView(APIView):
    def get(self, request):
        base_user = request.user
        search = request.query_params.get('search')
        status_param = request.query_params.get('status')
        project_id = request.query_params.get('project_id')
        active_param = request.query_params.get('active')
        priority_param = request.query_params.get('priority')

        tasks = TaskService.list_tasks(
            base_user,
            search=search,
            status=status_param,
            project_id=project_id,
            active=active_param,
            priority=priority_param
        )
        paginator = StandardResultsSetPagination()
        result_page = paginator.paginate_queryset(tasks, request)
        serializer = TaskSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        base_user = request.user
        serializer = TaskCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            task = TaskService.create_task(base_user, serializer.validated_data)
            return ApiResponse.success(
                message="Task created successfully",
                data=TaskSerializer(task).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            message = str(e)
            if hasattr(e, 'detail'):
                message = str(e.detail[0]) if isinstance(e.detail, list) else str(e.detail)
            return ApiResponse.error(message=message, status=status.HTTP_400_BAD_REQUEST)


class UserTaskDetailView(APIView):
    def get_object(self, user, task_id):
        try:
            return Task.objects.get(id=task_id, user=user)
        except Task.DoesNotExist:
            return None

    def get(self, request, task_id):
        base_user = request.user
        task = self.get_object(base_user, task_id)
        if not task:
            return ApiResponse.error(message="Task not found", status=status.HTTP_404_NOT_FOUND)

        return ApiResponse.success(
            message="Task details fetched successfully",
            data=TaskSerializer(task).data,
            status=status.HTTP_200_OK
        )

    def patch(self, request, task_id):
        base_user = request.user
        task = self.get_object(base_user, task_id)
        if not task:
            return ApiResponse.error(message="Task not found", status=status.HTTP_404_NOT_FOUND)

        serializer = TaskUpdateSerializer(task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            updated_task = TaskService.update_task(task, serializer.validated_data)
            return ApiResponse.success(
                message="Task updated successfully",
                data=TaskSerializer(updated_task).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            message = str(e)
            if hasattr(e, 'detail'):
                message = str(e.detail[0]) if isinstance(e.detail, list) else str(e.detail)
            return ApiResponse.error(message=message, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, task_id):
        base_user = request.user
        task = self.get_object(base_user, task_id)
        if not task:
            return ApiResponse.error(message="Task not found", status=status.HTTP_404_NOT_FOUND)

        TaskService.delete_task(task)
        return ApiResponse.success(
            message="Task archived successfully",
            status=status.HTTP_200_OK
        )
