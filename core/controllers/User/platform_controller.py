from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework import status
from common.responses import ApiResponse
from core.serializers.User.auth_serializer import UserLoginSerializer, UserProfileSerializer
from core.serializers.User.platform_serializer import NotificationSerializer, FileSerializer, WorkspaceSettingSerializer
from core.services.User.auth_service import UserAuthService
from core.services.User.platform_service import PlatformService
from core.models.platform import Notification

User = get_user_model()


def _error_message(e):
    if hasattr(e, 'detail'):
        detail = e.detail
        if isinstance(detail, list) and detail:
            return str(detail[0])
        return str(detail)
    return str(e)


class AuthLoginAliasView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            result = UserAuthService.login(**serializer.validated_data)
            data = {
                'access': result['access'],
                'refresh': result['refresh'],
                'user': UserProfileSerializer(result['user']).data,
            }
            return ApiResponse.success('Login successful', data)
        except Exception as e:
            return ApiResponse.error(_error_message(e), status.HTTP_400_BAD_REQUEST)


class AuthRefreshView(APIView):
    def post(self, request):
        refresh = request.data.get('refresh')
        if not refresh:
            return ApiResponse.error('Refresh token is required', status.HTTP_400_BAD_REQUEST)
        try:
            access = PlatformService.refresh_access_token(refresh)
            return ApiResponse.success('Token refreshed successfully', {'access': access})
        except Exception as e:
            return ApiResponse.error(_error_message(e), status.HTTP_400_BAD_REQUEST)


class AuthLogoutView(APIView):
    def post(self, request):
        PlatformService.logout()
        return ApiResponse.success('Logout successful')


class UserMeView(APIView):
    def get(self, request):
        return ApiResponse.success('User profile fetched successfully', UserProfileSerializer(request.user).data)


class NotificationListView(APIView):
    def get(self, request):
        notifications = PlatformService.list_notifications()
        return ApiResponse.success('Notifications fetched successfully', NotificationSerializer(notifications, many=True).data)


class NotificationReadView(APIView):
    def patch(self, request, id):
        notification = Notification.objects.filter(id=id).first()
        if not notification:
            return ApiResponse.error('Notification not found', status.HTTP_404_NOT_FOUND)
        notification = PlatformService.mark_notification_read(notification)
        return ApiResponse.success('Notification marked as read', NotificationSerializer(notification).data)


class FileUploadView(APIView):
    def post(self, request):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return ApiResponse.error('No file provided', status.HTTP_400_BAD_REQUEST)

        visibility = request.data.get('visibility', 'private')
        metadata = request.data.get('metadata_json')
        file = PlatformService.upload_file(file_obj, visibility=visibility, metadata=metadata)
        return ApiResponse.success('File uploaded successfully', FileSerializer(file).data, status.HTTP_201_CREATED)


class FileDetailView(APIView):
    def get(self, request, fileId):
        try:
            file, payload = PlatformService.get_file(fileId)
            payload['created_at'] = file.created_at
            payload['updated_at'] = file.updated_at
            return ApiResponse.success('File metadata fetched successfully', payload)
        except Exception as e:
            return ApiResponse.error(_error_message(e), status.HTTP_404_NOT_FOUND)


class WorkspaceSettingsView(APIView):
    def get(self, request):
        settings_obj = PlatformService.get_workspace_settings()
        return ApiResponse.success('Workspace settings fetched successfully', WorkspaceSettingSerializer(settings_obj).data)

    def patch(self, request):
        settings_obj = PlatformService.update_workspace_settings(request.data)
        return ApiResponse.success('Workspace settings updated successfully', WorkspaceSettingSerializer(settings_obj).data)


class HealthView(APIView):
    def get(self, request):
        return ApiResponse.success('Service is healthy', {'service': 'workhub-backend', 'status': 'ok'})
