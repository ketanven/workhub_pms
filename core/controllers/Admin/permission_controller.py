from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from core.authentication import AdminJWTAuthentication
from core.models import Role, Permission
from core.serializers.Admin.permission_serializer import PermissionSerializer
from common.responses import ApiResponse

class PermissionGroupedListView(APIView):
    authentication_classes = [AdminJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        permissions = Permission.objects.all()
        grouped_data = []
        # Extract unique groups
        group_names = set([p.group_name for p in permissions])
        for name in group_names:
            group_perms = [p for p in permissions if p.group_name == name]
            grouped_data.append({
                "group_name": name,
                "permissions": PermissionSerializer(group_perms, many=True).data
            })
            
        return ApiResponse.success("Permissions fetched successfully", data=grouped_data)

class RolePermissionAssignView(APIView):
    authentication_classes = [AdminJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
             role = Role.objects.get(pk=pk)
        except Role.DoesNotExist:
             return ApiResponse.error("Role not found", status=status.HTTP_404_NOT_FOUND)
             
        permission_codes = request.data.get('permission_codes', [])
        permissions = Permission.objects.filter(code__in=permission_codes)
        
        role.permissions.set(permissions)
        
        return ApiResponse.success("Permissions assigned successfully")
