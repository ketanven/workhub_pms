from django.urls import path
from core.controllers.Admin.auth_controller import (
    AdminLoginView, 
    AdminProfileView, 
    AdminChangePasswordView, 
    AdminForgotPasswordView
)

from django.utils.decorators import decorator_from_middleware
from core.middleware.admin_auth import AdminAuthMiddleware

admin_auth_required = decorator_from_middleware(AdminAuthMiddleware)

urlpatterns = [
    path('login/', AdminLoginView.as_view(), name='admin-login'),
    path('profile/', admin_auth_required(AdminProfileView.as_view()), name='admin-profile'),
    path('change-password/', admin_auth_required(AdminChangePasswordView.as_view()), name='admin-change-password'),
    path('forgot-password/', AdminForgotPasswordView.as_view(), name='admin-forgot-password'),
]
