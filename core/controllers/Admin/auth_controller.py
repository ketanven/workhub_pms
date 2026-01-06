from rest_framework.views import APIView
from rest_framework import status

from core.serializers.User.login_serializer import LoginSerializer
from core.services.Admin.auth_service import AdminAuthService
from common.responses import ApiResponse


class AdminAuthController(APIView):

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            data = AdminAuthService.login(serializer.validated_data)
            return ApiResponse.success(
                message="Admin login successful",
                data=data,
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return ApiResponse.error(
                message=str(e),
                status=status.HTTP_400_BAD_REQUEST
            )
