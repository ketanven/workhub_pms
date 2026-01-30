from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication

from core.serializers.Admin.auth_serializer import (
    AdminLoginSerializer, 
    AdminProfileSerializer, 
    UpdateProfileSerializer, 
    ChangePasswordSerializer,
    ForgotPasswordSerializer
)
from core.services.Admin.auth_service import AdminAuthService
from common.responses import ApiResponse


from core.authentication import AdminJWTAuthentication

class AdminLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AdminLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = AdminAuthService.login(**serializer.validated_data)
            data = {
                "access": result['access'],
                "refresh": result['refresh'],
                "user": AdminProfileSerializer(result['user']).data
            }
            return ApiResponse.success(
                message="Admin login successful",
                data=data,
                status=status.HTTP_200_OK
            )

        except Exception as e:
            message = str(e)
            if hasattr(e, 'detail'):
                if isinstance(e.detail, list):
                    message = str(e.detail[0])
                elif isinstance(e.detail, dict):
                    message = next(iter(e.detail.values()))[0] if e.detail else str(e)
                else:
                    message = str(e.detail)
            
            return ApiResponse.error(
                message=message,
                status=status.HTTP_400_BAD_REQUEST
            )

class AdminProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = AdminProfileSerializer(request.user)
        return ApiResponse.success(
            message="Profile fetched successfully",
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    def patch(self, request):
        serializer = UpdateProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        try:
            user = AdminAuthService.update_profile(request.user, serializer.validated_data)
            return ApiResponse.success(
                message="Profile updated successfully",
                data=AdminProfileSerializer(user).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            message = str(e)
            if hasattr(e, 'detail'):
                if isinstance(e.detail, list):
                    message = str(e.detail[0])
                elif isinstance(e.detail, dict):
                    message = next(iter(e.detail.values()))[0] if e.detail else str(e)
                else:
                    message = str(e.detail)
            return ApiResponse.error(
                message=message,
                status=status.HTTP_400_BAD_REQUEST
            )

class AdminChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            AdminAuthService.change_password(
                user=request.user, 
                old_password=serializer.validated_data['old_password'],
                new_password=serializer.validated_data['new_password']
            )
            return ApiResponse.success(
                message="Password changed successfully",
                status=status.HTTP_200_OK
            )
        except Exception as e:
            message = str(e)
            if hasattr(e, 'detail'):
                if isinstance(e.detail, list):
                    message = str(e.detail[0])
                elif isinstance(e.detail, dict):
                    message = next(iter(e.detail.values()))[0] if e.detail else str(e)
                else:
                    message = str(e.detail)
            return ApiResponse.error(
                message=message,
                status=status.HTTP_400_BAD_REQUEST
            )

class AdminForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            AdminAuthService.forgot_password(email=serializer.validated_data['email'])
            return ApiResponse.success(
                message="If the email exists, a password reset link has been sent.",
                status=status.HTTP_200_OK
            )
        except Exception as e:
            message = str(e)
            if hasattr(e, 'detail'):
                if isinstance(e.detail, list):
                    message = str(e.detail[0])
                elif isinstance(e.detail, dict):
                    message = next(iter(e.detail.values()))[0] if e.detail else str(e)
                else:
                    message = str(e.detail)
            return ApiResponse.error(
                message=message,
                status=status.HTTP_400_BAD_REQUEST
            )
