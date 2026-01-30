from rest_framework.exceptions import ValidationError
from core.models import Admin
import jwt
from django.conf import settings
from datetime import datetime

class AdminAuthService:
    @staticmethod
    def login(email, password):
        try:
            admin = Admin.objects.get(email=email)
        except Admin.DoesNotExist:
            raise ValidationError("Invalid credentials")

        if not admin.check_password(password):
             raise ValidationError("Invalid credentials")
        
        # Generate JWT Tokens
        access_token_payload = {
            'user_id': str(admin.id),
            'exp': datetime.utcnow() + settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
            'iat': datetime.utcnow()
        }
        access_token = jwt.encode(access_token_payload, settings.SECRET_KEY, algorithm='HS256')

        refresh_token_payload = {
            'user_id': str(admin.id),
            'exp': datetime.utcnow() + settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
            'iat': datetime.utcnow()
        }
        refresh_token = jwt.encode(refresh_token_payload, settings.SECRET_KEY, algorithm='HS256')

        return {
            "access": access_token,
            "refresh": refresh_token,
            "user": admin
        }

    @staticmethod
    def change_password(admin, old_password, new_password):
        if not admin.check_password(old_password):
            raise ValidationError("Incorrect old password")
        
        admin.set_password(new_password)
        admin.save()
        return admin

    @staticmethod
    def update_profile(admin, data):
        # Prevent role update through profile update
        if 'role' in data:
            data.pop('role')
        
        for key, value in data.items():
            setattr(admin, key, value)
        admin.save()
        return admin

    @staticmethod
    def forgot_password(email):
        try:
            admin = Admin.objects.get(email=email)
            # Logic to generate reset token and send email would go here
            return True
        except Admin.DoesNotExist:
             raise ValidationError("Email not found")
