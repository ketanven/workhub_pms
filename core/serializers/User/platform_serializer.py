from rest_framework import serializers
from core.models.platform import Notification, File, WorkspaceSetting


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'


class WorkspaceSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkspaceSetting
        fields = '__all__'


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = '__all__'
