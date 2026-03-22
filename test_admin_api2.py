from django.test import RequestFactory
from core.controllers.Admin.auth_controller import AdminProfileView
from core.models import Admin
import jwt
from django.conf import settings
from datetime import datetime
import traceback

try:
    admin = Admin.objects.get(email="admin@workhub.com")

    payload = {
        'user_id': str(admin.id),
        'exp': datetime.utcnow() + settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

    factory = RequestFactory()
    request = factory.get('/api/admin/profile/', HTTP_AUTHORIZATION=f'Bearer {token}')

    view = AdminProfileView.as_view()
    response = view(request)
    if hasattr(response, 'data'):
        print(response.data)
    else:
        print("Response content:", response.content)
except Exception as e:
    traceback.print_exc()
