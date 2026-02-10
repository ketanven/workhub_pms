from django.db.models import Q
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from core.models.task import Task
from core.models.project import Project


class TaskService:
    @staticmethod
    def list_tasks(user, search=None, status=None, project_id=None, active=None, priority=None):
        queryset = Task.objects.filter(user=user).order_by('-created_at')

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )

        if status:
            queryset = queryset.filter(status=status)

        if priority:
            queryset = queryset.filter(priority=priority)

        if project_id:
            queryset = queryset.filter(project_id=project_id)

        if active is not None:
            is_active = str(active).lower() == 'true'
            queryset = queryset.filter(is_active=is_active)

        return queryset

    @staticmethod
    def _validate_project(user, project):
        if project.user_id != user.id:
            raise ValidationError("Project does not belong to the user.")
        if not project.is_active:
            raise ValidationError("Project is archived.")

    @staticmethod
    def create_task(user, data):
        project = data.get('project')
        if not isinstance(project, Project):
            raise ValidationError("Project is required.")
        TaskService._validate_project(user, project)

        task = Task.objects.create(user=user, **data)
        return task

    @staticmethod
    def update_task(task, data):
        if 'project' in data and data['project'] is not None:
            TaskService._validate_project(task.user, data['project'])

        for key, value in data.items():
            setattr(task, key, value)
        task.save()
        return task

    @staticmethod
    def delete_task(task):
        task.is_active = False
        task.archived_at = timezone.now()
        task.save()
        return task
