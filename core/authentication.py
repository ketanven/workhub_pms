from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
import jwt
from core.models import Admin

class AdminJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None

        try:
            # Header format: "Bearer <token>"
            prefix, token = auth_header.split(' ')
            if prefix != 'Bearer':
                raise AuthenticationFailed('Authorization header must start with Bearer')
        except ValueError:
             raise AuthenticationFailed('Invalid authorization header format')

        try:
            # Decode the token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')

        # Check if the token is for an Admin
        user_id = payload.get('user_id')
        if not user_id:
            raise AuthenticationFailed('Invalid token payload')

        try:
            admin = Admin.objects.get(id=user_id)
        except Admin.DoesNotExist:
            raise AuthenticationFailed('User not found')

        if not admin.is_active:
            raise AuthenticationFailed('User is inactive')

        return (admin, None)
