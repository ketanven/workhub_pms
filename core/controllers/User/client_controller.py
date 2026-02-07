from rest_framework.views import APIView
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from common.responses import ApiResponse
from core.models.client import Client
from core.serializers.User.client_serializer import (
    ClientSerializer,
    ClientCreateSerializer,
    ClientUpdateSerializer
)
from core.services.User.client_service import ClientService


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class UserClientListView(APIView):
    def get(self, request):
        base_user = request.user
        search = request.query_params.get('search')
        status_param = request.query_params.get('status')

        clients = ClientService.list_clients(base_user, search, status_param)
        paginator = StandardResultsSetPagination()
        result_page = paginator.paginate_queryset(clients, request)
        serializer = ClientSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        base_user = request.user
        serializer = ClientCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            client = ClientService.create_client(base_user, serializer.validated_data)
            return ApiResponse.success(
                message="Client created successfully",
                data=ClientSerializer(client).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            message = str(e)
            if hasattr(e, 'detail'):
                message = str(e.detail[0]) if isinstance(e.detail, list) else str(e.detail)
            return ApiResponse.error(message=message, status=status.HTTP_400_BAD_REQUEST)


class UserClientDetailView(APIView):
    def get_object(self, user, client_id):
        try:
            return Client.objects.get(id=client_id, user=user)
        except Client.DoesNotExist:
            return None

    def get(self, request, client_id):
        base_user = request.user
        client = self.get_object(base_user, client_id)
        if not client:
            return ApiResponse.error(message="Client not found", status=status.HTTP_404_NOT_FOUND)

        return ApiResponse.success(
            message="Client details fetched successfully",
            data=ClientSerializer(client).data,
            status=status.HTTP_200_OK
        )

    def patch(self, request, client_id):
        base_user = request.user
        client = self.get_object(base_user, client_id)
        if not client:
            return ApiResponse.error(message="Client not found", status=status.HTTP_404_NOT_FOUND)

        serializer = ClientUpdateSerializer(client, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            updated_client = ClientService.update_client(client, serializer.validated_data)
            return ApiResponse.success(
                message="Client updated successfully",
                data=ClientSerializer(updated_client).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            message = str(e)
            if hasattr(e, 'detail'):
                message = str(e.detail[0]) if isinstance(e.detail, list) else str(e.detail)
            return ApiResponse.error(message=message, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, client_id):
        base_user = request.user
        client = self.get_object(base_user, client_id)
        if not client:
            return ApiResponse.error(message="Client not found", status=status.HTTP_404_NOT_FOUND)

        ClientService.delete_client(client)
        return ApiResponse.success(
            message="Client archived successfully",
            status=status.HTTP_200_OK
        )
