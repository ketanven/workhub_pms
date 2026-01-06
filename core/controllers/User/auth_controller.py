from rest_framework.views import APIView
from rest_framework.response import Response
from core.serializers.User.login_serializer import LoginSerializer

class UserAuthController(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"message": "User login OK"})
