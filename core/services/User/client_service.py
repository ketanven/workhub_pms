from django.db.models import Q
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from core.models.client import Client


class ClientService:
    @staticmethod
    def list_clients(user, search=None, status=None):
        queryset = Client.objects.filter(user=user).order_by('-created_at')

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(company_name__icontains=search) |
                Q(email__icontains=search)
            )

        if status is not None:
            is_active = str(status).lower() == 'true'
            queryset = queryset.filter(is_active=is_active)

        return queryset

    @staticmethod
    def create_client(user, data):
        if data.get('email'):
            exists = Client.objects.filter(user=user, email=data['email'], is_active=True).exists()
            if exists:
                raise ValidationError("Client with this email already exists.")

        client = Client.objects.create(user=user, **data)
        return client

    @staticmethod
    def update_client(client, data):
        if 'email' in data and data['email']:
            exists = Client.objects.filter(
                user=client.user,
                email=data['email'],
                is_active=True
            ).exclude(id=client.id).exists()
            if exists:
                raise ValidationError("Client with this email already exists.")

        for key, value in data.items():
            setattr(client, key, value)
        client.save()
        return client

    @staticmethod
    def delete_client(client):
        client.is_active = False
        client.archived_at = timezone.now()
        client.save()
        return client
