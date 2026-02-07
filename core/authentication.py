import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

User = get_user_model()
try:
    from core.models import Admin
except Exception:
    Admin = None


class UserJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            auth_header = request.META.get('HTTP_AUTHORIZATION') or request.META.get('Authorization')
        if not auth_header:
            return None

        parts = auth_header.strip().split()
        if len(parts) != 2:
            raise AuthenticationFailed('Invalid authorization header format')
        prefix, token = parts
        if prefix not in ('Bearer', 'Token'):
            raise AuthenticationFailed('Authorization header must start with Bearer')

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')

        user_id = payload.get('user_id')
        if not user_id:
            raise AuthenticationFailed('Invalid token payload')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found')

        if not user.is_active:
            raise AuthenticationFailed('User is inactive')

        return (user, None)


class AdminJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        if Admin is None:
            raise AuthenticationFailed('Admin model not available')

        auth_header = request.headers.get('Authorization')
        if not auth_header:
            auth_header = request.META.get('HTTP_AUTHORIZATION') or request.META.get('Authorization')
        if not auth_header:
            return None

        parts = auth_header.strip().split()
        if len(parts) != 2:
            raise AuthenticationFailed('Invalid authorization header format')
        prefix, token = parts
        if prefix not in ('Bearer', 'Token'):
            raise AuthenticationFailed('Authorization header must start with Bearer')

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')

        user_id = payload.get('user_id')
        if not user_id:
            raise AuthenticationFailed('Invalid token payload')

        try:
            admin = Admin.objects.get(id=user_id)
        except Admin.DoesNotExist:
            raise AuthenticationFailed('Admin not found')

        if not admin.is_active:
            raise AuthenticationFailed('Admin is inactive')

        return (admin, None)
