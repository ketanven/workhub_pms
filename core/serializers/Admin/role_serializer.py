from rest_framework import serializers
from core.models import Role
from .permission_serializer import PermissionSerializer

class RoleListSerializer(serializers.ModelSerializer):
    permissions_count = serializers.SerializerMethodField()
    assigned_admins_count = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = ['id', 'name', 'permissions_count', 'assigned_admins_count', 'created_at']

    def get_permissions_count(self, obj):
        return obj.permissions.count()

    def get_assigned_admins_count(self, obj):
        return obj.admins.count()

class RoleDetailSerializer(serializers.ModelSerializer):
    permissions = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='code'
    )

    class Meta:
        model = Role
        fields = ['id', 'name', 'permissions', 'created_at']

class RoleCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name']
