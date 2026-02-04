from django.urls import path
from core.controllers.Admin.auth_controller import (
    AdminLoginView, 
    AdminProfileView, 
    AdminChangePasswordView, 
    AdminChangePasswordView,
    AdminForgotPasswordView
)
from core.controllers.Admin.user_controller import AdminUserListView, AdminUserDetailView

from django.utils.decorators import decorator_from_middleware
from core.middleware.admin_auth import AdminAuthMiddleware

admin_auth_required = decorator_from_middleware(AdminAuthMiddleware)

urlpatterns = [
    path('login/', AdminLoginView.as_view(), name='admin-login'),
    path('profile/', admin_auth_required(AdminProfileView.as_view()), name='admin-profile'),
    path('change-password/', admin_auth_required(AdminChangePasswordView.as_view()), name='admin-change-password'),
    path('forgot-password/', AdminForgotPasswordView.as_view(), name='admin-forgot-password'),
    
    # User Management
    path('users/', admin_auth_required(AdminUserListView.as_view()), name='admin-user-list'),
    path('users/<int:pk>/', admin_auth_required(AdminUserDetailView.as_view()), name='admin-user-detail'),
]
