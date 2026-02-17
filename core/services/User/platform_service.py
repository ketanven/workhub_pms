import hashlib
import os
from django.core.files.storage import default_storage
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from core.models.platform import Notification, File, WorkspaceSetting


class PlatformService:
    @staticmethod
    def refresh_access_token(refresh_token):
        import jwt
        from django.conf import settings

        try:
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise ValidationError('Refresh token has expired')
        except jwt.InvalidTokenError:
            raise ValidationError('Invalid refresh token')

        user_id = payload.get('user_id')
        if not user_id:
            raise ValidationError('Invalid refresh token payload')

        access_token = jwt.encode(
            {
                'user_id': user_id,
                'exp': timezone.now() + settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
                'iat': timezone.now(),
            },
            settings.SECRET_KEY,
            algorithm='HS256',
        )
        return access_token

    @staticmethod
    def logout():
        return True

    @staticmethod
    def list_notifications():
        return Notification.objects.all().order_by('-created_at')

    @staticmethod
    def mark_notification_read(notification):
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        return notification

    @staticmethod
    def upload_file(uploaded_file, visibility='private', metadata=None):
        metadata = metadata or {}
        ext = os.path.splitext(uploaded_file.name)[1].lower().replace('.', '')
        file_key = f"uploads/{timezone.now().strftime('%Y/%m/%d')}/{uploaded_file.name}"

        saved_path = default_storage.save(file_key, uploaded_file)
        uploaded_file.seek(0)
        checksum = hashlib.sha256(uploaded_file.read()).hexdigest()

        return File.objects.create(
            storage_disk='default',
            path=saved_path,
            original_name=uploaded_file.name,
            mime_type=getattr(uploaded_file, 'content_type', '') or '',
            extension=ext,
            size_bytes=uploaded_file.size,
            checksum=checksum,
            visibility=visibility,
            status='uploaded',
            metadata_json=metadata,
            uploaded_at=timezone.now(),
        )

    @staticmethod
    def get_file(file_id):
        file = File.objects.filter(id=file_id).first()
        if not file:
            raise ValidationError('File not found')
        file_data = {
            'id': str(file.id),
            'path': file.path,
            'original_name': file.original_name,
            'mime_type': file.mime_type,
            'size_bytes': file.size_bytes,
            'visibility': file.visibility,
            'download_url': default_storage.url(file.path) if file.path else '',
        }
        return file, file_data

    @staticmethod
    def get_workspace_settings():
        settings_obj = WorkspaceSetting.objects.order_by('-id').first()
        if settings_obj:
            return settings_obj
        return WorkspaceSetting.objects.create()

    @staticmethod
    def update_workspace_settings(data):
        settings_obj = PlatformService.get_workspace_settings()
        for key, value in data.items():
            setattr(settings_obj, key, value)
        settings_obj.save()
        return settings_obj
