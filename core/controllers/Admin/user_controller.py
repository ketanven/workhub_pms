from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import get_user_model
from core.serializers.Admin.user_serializer import (
    AdminUserSerializer, 
    AdminUserCreateSerializer, 
    AdminUserUpdateSerializer
)
from core.services.Admin.user_service import AdminUserService
from common.responses import ApiResponse
from rest_framework.pagination import PageNumberPagination

User = get_user_model()

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

class AdminUserListView(APIView):
    # Middleware handles auth

    def get(self, request):
        search = request.query_params.get('search')
        status_param = request.query_params.get('status')
        
        users = AdminUserService.list_users(search, status_param)
        paginator = StandardResultsSetPagination()
        result_page = paginator.paginate_queryset(users, request)
        serializer = AdminUserSerializer(result_page, many=True)
        
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = AdminUserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            user = AdminUserService.create_user(serializer.validated_data)
            return ApiResponse.success(
                message="User created successfully",
                data=AdminUserSerializer(user).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            message = str(e)
            if hasattr(e, 'detail'):
                message = str(e.detail[0]) if isinstance(e.detail, list) else str(e.detail)
            return ApiResponse.error(message=message, status=status.HTTP_400_BAD_REQUEST)

class AdminUserDetailView(APIView):
    # Middleware handles auth

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            return None

    def get(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return ApiResponse.error(message="User not found", status=status.HTTP_404_NOT_FOUND)
            
        serializer = AdminUserSerializer(user)
        return ApiResponse.success(
            message="User details fetched successfully",
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    def patch(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return ApiResponse.error(message="User not found", status=status.HTTP_404_NOT_FOUND)

        serializer = AdminUserUpdateSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        try:
            updated_user = AdminUserService.update_user(user, serializer.validated_data)
            return ApiResponse.success(
                message="User updated successfully",
                data=AdminUserSerializer(updated_user).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            message = str(e)
            if hasattr(e, 'detail'):
                 message = str(e.detail[0]) if isinstance(e.detail, list) else str(e.detail)
            return ApiResponse.error(message=message, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user = self.get_object(pk)
        if not user:
             return ApiResponse.error(message="User not found", status=status.HTTP_404_NOT_FOUND)
        
        AdminUserService.delete_user(user)
        return ApiResponse.success(
            message="User archived successfully",
            status=status.HTTP_200_OK
        )
