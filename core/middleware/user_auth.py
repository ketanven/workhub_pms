import jwt
import logging
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model
from common.responses import ApiResponse

User = get_user_model()
logger = logging.getLogger(__name__)

class UserAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        try:
            raw_auth = request.headers.get('Authorization')
            if not raw_auth:
                raw_auth = request.META.get('HTTP_AUTHORIZATION') or request.META.get('Authorization')
            masked = None
            if raw_auth:
                parts = raw_auth.split()
                if len(parts) == 2:
                    token = parts[1]
                    masked = f"{parts[0]} {token[:8]}...{token[-6:]}"
                else:
                    masked = raw_auth[:8] + "..."
            msg = f"[UserAuthMiddleware] path={request.path} auth={masked} content_type={request.content_type}"
            logger.warning(msg)
            print(msg)
        except Exception as _e:
            logger.warning(f"[UserAuthMiddleware] debug log failed: {_e}")

        auth_header = request.headers.get('Authorization')
        if not auth_header:
            auth_header = request.META.get('HTTP_AUTHORIZATION') or request.META.get('Authorization')
        if not auth_header:
            return ApiResponse.json_error(message='Authentication credentials were not provided.', status=401)

        try:
            # Header format: "Bearer <token>"
            parts = auth_header.strip().split()
            if len(parts) != 2:
                return ApiResponse.json_error(message='Invalid authorization header format', status=401)
            prefix, token = parts
            if prefix not in ('Bearer', 'Token'):
                return ApiResponse.json_error(message='Authorization header must start with Bearer', status=401)
        except Exception:
            return ApiResponse.json_error(message='Invalid authorization header format', status=401)

        try:
            # Decode the token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return ApiResponse.json_error(message='Token has expired', status=401)
        except jwt.InvalidTokenError:
            return ApiResponse.json_error(message='Invalid token', status=401)

        # Check if the token is for a User
        user_id = payload.get('user_id')
        if not user_id:
            return ApiResponse.json_error(message='Invalid token payload', status=401)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return ApiResponse.json_error(message='User not found', status=401)

        if not user.is_active:
            return ApiResponse.json_error(message='User is inactive', status=401)

        # Attach the user to the request (override any cached/anonymous user)
        request.user = user
        try:
            request._cached_user = user
        except Exception:
            pass

        try:
            logger.warning(f"[UserAuthMiddleware] resolved_user_id={user.id} is_active={user.is_active}")
            print(f"[UserAuthMiddleware] resolved_user_id={user.id} is_active={user.is_active}")
        except Exception:
            pass
        return None
