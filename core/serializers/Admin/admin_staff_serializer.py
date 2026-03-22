from rest_framework import serializers
from core.models import Admin
from django.contrib.auth.hashers import make_password
from .role_serializer import RoleDetailSerializer

class AdminStaffListSerializer(serializers.ModelSerializer):
    role = RoleDetailSerializer(read_only=True)
    
    class Meta:
        model = Admin
        fields = ['id', 'first_name', 'last_name', 'email', 'role', 'is_active', 'created_at']

class AdminStaffCreateUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Admin
        fields = ['id', 'first_name', 'last_name', 'email', 'password', 'role', 'is_active']
        
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        admin = super().create(validated_data)
        if password:
            admin.set_password(password)
            admin.save(update_fields=['password'])
        return admin

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        admin = super().update(instance, validated_data)
        if password:
            admin.set_password(password)
            admin.save(update_fields=['password'])
        return admin
