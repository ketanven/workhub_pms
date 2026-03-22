from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from core.authentication import AdminJWTAuthentication
from core.models import Role
from core.serializers.Admin.role_serializer import RoleListSerializer, RoleDetailSerializer, RoleCreateUpdateSerializer
from common.responses import ApiResponse

class RoleListView(generics.ListCreateAPIView):
    authentication_classes = [AdminJWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Role.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RoleCreateUpdateSerializer
        return RoleListSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return ApiResponse.success("Roles fetched successfully", data=serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        role = serializer.save()
        response_serializer = RoleDetailSerializer(role)
        return ApiResponse.success("Role created successfully", data=response_serializer.data, status=status.HTTP_201_CREATED)

class RoleDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [AdminJWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Role.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return RoleCreateUpdateSerializer
        return RoleDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return ApiResponse.success("Role fetched successfully", data=serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        role = serializer.save()
        response_serializer = RoleDetailSerializer(role)
        return ApiResponse.success("Role updated successfully", data=response_serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.admins.exists():
             return ApiResponse.error("Cannot delete role assigned to admins", status=status.HTTP_400_BAD_REQUEST)
        instance.delete()
        return ApiResponse.success("Role deleted successfully")
