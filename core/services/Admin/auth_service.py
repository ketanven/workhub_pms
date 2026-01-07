from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed

class AdminAuthService:

    @staticmethod
    def login(validated_data):
        email = validated_data.get('email')
        password = validated_data.get('password')

        user = authenticate(email=email, password=password)

        if not user:
            raise AuthenticationFailed("Invalid email or password provided.")

        if user.role != 'admin':
            raise AuthenticationFailed("Access denied. Admin only.")

        return {
            "id": user.id,
            "email": user.email,
            "role": user.role
        }
