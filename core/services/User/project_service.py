from django.db.models import Q
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from core.models.project import Project
from core.models.client import Client


class ProjectService:
    @staticmethod
    def list_projects(user, search=None, status=None, client_id=None, active=None):
        queryset = Project.objects.filter(user=user).order_by('-created_at')

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        if status:
            queryset = queryset.filter(status=status)

        if client_id:
            queryset = queryset.filter(client_id=client_id)

        if active is not None:
            is_active = str(active).lower() == 'true'
            queryset = queryset.filter(is_active=is_active)

        return queryset

    @staticmethod
    def _validate_client(user, client):
        if client.user_id != user.id:
            raise ValidationError("Client does not belong to the user.")
        if not client.is_active:
            raise ValidationError("Client is archived.")

    @staticmethod
    def create_project(user, data):
        client = data.get('client')
        if not isinstance(client, Client):
            raise ValidationError("Client is required.")
        ProjectService._validate_client(user, client)

        project = Project.objects.create(user=user, **data)
        return project

    @staticmethod
    def update_project(project, data):
        if 'client' in data and data['client'] is not None:
            ProjectService._validate_client(project.user, data['client'])

        for key, value in data.items():
            setattr(project, key, value)
        project.save()
        return project

    @staticmethod
    def delete_project(project):
        project.is_active = False
        project.archived_at = timezone.now()
        project.save()
        return project
