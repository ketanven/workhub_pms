from django.db import models
from .project import Project
from .user import User

class Task(models.Model):
    title = models.CharField(max_length=255)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title
