from django.urls import path
from core.controllers.Admin.auth_controller import AdminAuthController

urlpatterns = [
    path('login/', AdminAuthController.as_view(), name='admin-login'),
]
