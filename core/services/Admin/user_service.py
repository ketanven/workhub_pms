from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from django.db.models import Q

User = get_user_model()

class AdminUserService:
    @staticmethod
    def list_users(search=None, status=None):
        queryset = User.objects.all().order_by('-date_joined')
        
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) | 
                Q(last_name__icontains=search) | 
                Q(email__icontains=search)
            )
        
        if status is not None:
             # Normalize status to boolean
            is_active = str(status).lower() == 'true'
            queryset = queryset.filter(is_active=is_active)
            
        return queryset

    @staticmethod
    def create_user(data):
        if User.objects.filter(email=data['email']).exists():
            raise ValidationError("User with this email already exists.")
        
        username = data['email'].split('@')[0]
        # Handle potential username conflict
        if User.objects.filter(username=username).exists():
             import random
             username = f"{username}{random.randint(1, 9999)}"

        user = User.objects.create_user(
            username=username,
            email=data['email'],
            password=data['password'],
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', '')
        )
        return user

    @staticmethod
    def update_user(user, data):
        if 'email' in data and User.objects.filter(email=data['email']).exclude(id=user.id).exists():
             raise ValidationError("User with this email already exists.")
             
        for key, value in data.items():
            setattr(user, key, value)
        user.save()
        return user

    @staticmethod
    def delete_user(user):
        # Soft delete
        user.is_active = False
        user.save()
        return user
