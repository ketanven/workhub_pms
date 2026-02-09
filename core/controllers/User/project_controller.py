from rest_framework.views import APIView
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from common.responses import ApiResponse
from core.models.project import Project
from core.serializers.User.project_serializer import (
    ProjectSerializer,
    ProjectCreateSerializer,
    ProjectUpdateSerializer
)
from core.services.User.project_service import ProjectService


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class UserProjectListView(APIView):
    def get(self, request):
        base_user = request.user
        search = request.query_params.get('search')
        status_param = request.query_params.get('status')
        client_id = request.query_params.get('client_id')
        active_param = request.query_params.get('active')

        projects = ProjectService.list_projects(
            base_user,
            search=search,
            status=status_param,
            client_id=client_id,
            active=active_param
        )
        paginator = StandardResultsSetPagination()
        result_page = paginator.paginate_queryset(projects, request)
        serializer = ProjectSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        base_user = request.user
        serializer = ProjectCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            project = ProjectService.create_project(base_user, serializer.validated_data)
            return ApiResponse.success(
                message="Project created successfully",
                data=ProjectSerializer(project).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            message = str(e)
            if hasattr(e, 'detail'):
                message = str(e.detail[0]) if isinstance(e.detail, list) else str(e.detail)
            return ApiResponse.error(message=message, status=status.HTTP_400_BAD_REQUEST)


class UserProjectDetailView(APIView):
    def get_object(self, user, project_id):
        try:
            return Project.objects.get(id=project_id, user=user)
        except Project.DoesNotExist:
            return None

    def get(self, request, project_id):
        base_user = request.user
        project = self.get_object(base_user, project_id)
        if not project:
            return ApiResponse.error(message="Project not found", status=status.HTTP_404_NOT_FOUND)

        return ApiResponse.success(
            message="Project details fetched successfully",
            data=ProjectSerializer(project).data,
            status=status.HTTP_200_OK
        )

    def patch(self, request, project_id):
        base_user = request.user
        project = self.get_object(base_user, project_id)
        if not project:
            return ApiResponse.error(message="Project not found", status=status.HTTP_404_NOT_FOUND)

        serializer = ProjectUpdateSerializer(project, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            updated_project = ProjectService.update_project(project, serializer.validated_data)
            return ApiResponse.success(
                message="Project updated successfully",
                data=ProjectSerializer(updated_project).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            message = str(e)
            if hasattr(e, 'detail'):
                message = str(e.detail[0]) if isinstance(e.detail, list) else str(e.detail)
            return ApiResponse.error(message=message, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, project_id):
        base_user = request.user
        project = self.get_object(base_user, project_id)
        if not project:
            return ApiResponse.error(message="Project not found", status=status.HTTP_404_NOT_FOUND)

        ProjectService.delete_project(project)
        return ApiResponse.success(
            message="Project archived successfully",
            status=status.HTTP_200_OK
        )
