from django.urls import path
from core.controllers.Admin.auth_controller import (
    AdminLoginView, 
    AdminProfileView, 
    AdminChangePasswordView, 
    AdminChangePasswordView,
    AdminForgotPasswordView
)
from core.controllers.Admin.user_controller import AdminUserListView, AdminUserDetailView, AdminUserWorkspaceView

from core.controllers.Admin.role_controller import RoleListView, RoleDetailView
from core.controllers.Admin.permission_controller import PermissionGroupedListView, RolePermissionAssignView
from core.controllers.Admin.admin_staff_controller import AdminStaffListView, AdminStaffDetailView, AdminStaffToggleStatusView
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
    path('users/<int:pk>/workspace/', admin_auth_required(AdminUserWorkspaceView.as_view()), name='admin-user-workspace'),

    # Role & Permissions Management
    path('roles/', admin_auth_required(RoleListView.as_view()), name='admin-role-list'),
    path('roles/<uuid:pk>/', admin_auth_required(RoleDetailView.as_view()), name='admin-role-detail'),
    path('permissions/', admin_auth_required(PermissionGroupedListView.as_view()), name='admin-permission-list'),
    path('roles/<uuid:pk>/permissions/', admin_auth_required(RolePermissionAssignView.as_view()), name='admin-role-permission-assign'),

    # Admin Staff Management
    path('staff/', admin_auth_required(AdminStaffListView.as_view()), name='admin-staff-list'),
    path('staff/<uuid:pk>/', admin_auth_required(AdminStaffDetailView.as_view()), name='admin-staff-detail'),
    path('staff/<uuid:pk>/toggle-status/', admin_auth_required(AdminStaffToggleStatusView.as_view()), name='admin-staff-toggle-status'),
]
