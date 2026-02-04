from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
import random
import jwt
from django.conf import settings

User = get_user_model()

class UserAuthService:
    @staticmethod
    def register(data):
        if User.objects.filter(email=data['email']).exists():
            raise ValidationError("User with this email already exists.")
        
        username = data['email'].split('@')[0]
        # Handle potential username conflict
        if User.objects.filter(username=username).exists():
            username = f"{username}{random.randint(1, 9999)}"

        user = User.objects.create_user(
            username=username,
            email=data['email'],
            password=data['password'],
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', '')
        )
        
        # Generate JWT tokens
        access_token = jwt.encode({
            'user_id': str(user.id),
            'exp': timezone.now() + settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
            'iat': timezone.now()
        }, settings.SECRET_KEY, algorithm='HS256')
        
        refresh_token = jwt.encode({
            'user_id': str(user.id),
            'exp': timezone.now() + settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
            'iat': timezone.now()
        }, settings.SECRET_KEY, algorithm='HS256')
        
        return {
            "access": access_token,
            "refresh": refresh_token,
            "user": user
        }

    @staticmethod
    def login(email, password):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValidationError("Invalid credentials")

        if not user.check_password(password):
            raise ValidationError("Invalid credentials")
        
        if not user.is_active:
            raise ValidationError("Account is inactive")
        
        # Generate JWT tokens
        access_token = jwt.encode({
            'user_id': str(user.id),
            'exp': timezone.now() + settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
            'iat': timezone.now()
        }, settings.SECRET_KEY, algorithm='HS256')
        
        refresh_token = jwt.encode({
            'user_id': str(user.id),
            'exp': timezone.now() + settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
            'iat': timezone.now()
        }, settings.SECRET_KEY, algorithm='HS256')
        
        return {
            "access": access_token,
            "refresh": refresh_token,
            "user": user
        }

    @staticmethod
    def update_profile(user, data):
        if 'email' in data and User.objects.filter(email=data['email']).exclude(id=user.id).exists():
            raise ValidationError("User with this email already exists.")
        
        for key, value in data.items():
            setattr(user, key, value)
        user.save()
        return user

    @staticmethod
    def change_password(user, old_password, new_password):
        if not user.check_password(old_password):
            raise ValidationError("Old password is incorrect")
        
        user.set_password(new_password)
        user.save()
        return user

    @staticmethod
    def forgot_password(email):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValidationError("User with this email does not exist")
        
        # Generate 6-digit OTP
        otp = str(random.randint(100000, 999999))
        user.otp_code = otp
        user.otp_expiry = timezone.now() + timedelta(minutes=10)  # OTP valid for 10 minutes
        user.save()
        
        # TODO: Send email with OTP (for now just return it)
        return {"otp": otp, "message": "OTP sent to email"}

    @staticmethod
    def reset_password(email, otp, new_password):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValidationError("User with this email does not exist")
        
        if not user.otp_code or user.otp_code != otp:
            raise ValidationError("Invalid OTP")
        
        if not user.otp_expiry or timezone.now() > user.otp_expiry:
            raise ValidationError("OTP has expired")
        
        user.set_password(new_password)
        user.otp_code = None
        user.otp_expiry = None
        user.save()
        
        return user
