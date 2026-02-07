import jwt
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from core.models import Admin
from common.responses import ApiResponse
from datetime import datetime

class AdminAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
             print("No auth header")
             return ApiResponse.json_error(message='Authentication credentials were not provided.', status=401)

        try:
             # Header format: "Bearer <token>"
            prefix, token = auth_header.split(' ')
            if prefix != 'Bearer':
                 return ApiResponse.json_error(message='Authorization header must start with Bearer', status=401)
        except ValueError:
             return ApiResponse.json_error(message='Invalid authorization header format', status=401)

        try:
            # Decode the token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
             return ApiResponse.json_error(message='Token has expired', status=401)
        except jwt.InvalidTokenError:
             return ApiResponse.json_error(message='Invalid token', status=401)

        # Check if the token is for an Admin
        user_id = payload.get('user_id')
        if not user_id:
             return ApiResponse.json_error(message='Invalid token payload', status=401)

        try:
            admin = Admin.objects.get(id=user_id)
        except Admin.DoesNotExist:
             return ApiResponse.json_error(message='User not found', status=401)

        if not admin.is_active:
             return ApiResponse.json_error(message='User is inactive', status=401)

        # Attach the admin user to the request
        request.user = admin
        return None
