from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from core.serializers.User.auth_serializer import (
    UserRegisterSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UpdateProfileSerializer,
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer
)
from core.authentication import UserJWTAuthentication
from core.services.User.auth_service import UserAuthService
from common.responses import ApiResponse

class UserRegisterView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            result = UserAuthService.register(serializer.validated_data)
            data = {
                "access": result['access'],
                "refresh": result['refresh'],
                "user": UserProfileSerializer(result['user']).data
            }
            return ApiResponse.success(
                message="User registered successfully",
                data=data,
                status=status.HTTP_201_CREATED
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

class UserLoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            result = UserAuthService.login(**serializer.validated_data)
            data = {
                "access": result['access'],
                "refresh": result['refresh'],
                "user": UserProfileSerializer(result['user']).data
            }
            return ApiResponse.success(
                message="Login successful",
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

class UserProfileView(APIView):
    authentication_classes = [UserJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return ApiResponse.success(
            message="Profile fetched successfully",
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    def patch(self, request):
        serializer = UpdateProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        try:
            user = UserAuthService.update_profile(request.user, serializer.validated_data)
            return ApiResponse.success(
                message="Profile updated successfully",
                data=UserProfileSerializer(user).data,
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

class UserChangePasswordView(APIView):
    authentication_classes = [UserJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            UserAuthService.change_password(
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

class UserForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            result = UserAuthService.forgot_password(serializer.validated_data['email'])
            return ApiResponse.success(
                message=result['message'],
                data={"otp": result['otp']},  # Remove this in production
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

class UserResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            UserAuthService.reset_password(
                email=serializer.validated_data['email'],
                otp=serializer.validated_data['otp'],
                new_password=serializer.validated_data['new_password']
            )
            return ApiResponse.success(
                message="Password reset successfully",
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
