from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from core.authentication import AdminJWTAuthentication
from core.models import Admin
from core.serializers.Admin.admin_staff_serializer import AdminStaffListSerializer, AdminStaffCreateUpdateSerializer
from common.responses import ApiResponse

class AdminStaffListView(generics.ListCreateAPIView):
    authentication_classes = [AdminJWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Admin.objects.all().order_by('-created_at')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AdminStaffCreateUpdateSerializer
        return AdminStaffListSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return ApiResponse.success("Admin staff fetched successfully", data=serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        admin = serializer.save()
        response_serializer = AdminStaffListSerializer(admin)
        return ApiResponse.success("Admin staff created successfully", data=response_serializer.data, status=status.HTTP_201_CREATED)

class AdminStaffDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [AdminJWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Admin.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return AdminStaffCreateUpdateSerializer
        return AdminStaffListSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return ApiResponse.success("Admin staff fetched successfully", data=serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        admin = serializer.save()
        response_serializer = AdminStaffListSerializer(admin)
        return ApiResponse.success("Admin staff updated successfully", data=response_serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.id == request.user.id:
            return ApiResponse.error("You cannot delete yourself", status=status.HTTP_400_BAD_REQUEST)
        instance.delete()
        return ApiResponse.success("Admin staff deleted successfully")

class AdminStaffToggleStatusView(APIView):
    authentication_classes = [AdminJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
             admin = Admin.objects.get(pk=pk)
             if admin.id == request.user.id:
                 return ApiResponse.error("You cannot toggle your own status", status=status.HTTP_400_BAD_REQUEST)
                 
             admin.is_active = not admin.is_active
             admin.save()
             return ApiResponse.success(f"Admin status {'enabled' if admin.is_active else 'disabled'} successfully")
        except Admin.DoesNotExist:
             return ApiResponse.error("Admin not found", status=status.HTTP_404_NOT_FOUND)
