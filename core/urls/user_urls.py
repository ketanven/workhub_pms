from django.urls import path
from core.controllers.User.auth_controller import (
    UserRegisterView,
    UserLoginView,
    UserProfileView,
    UserChangePasswordView,
    UserForgotPasswordView,
    UserResetPasswordView
)
from core.controllers.User.client_controller import (
    UserClientListView,
    UserClientDetailView
)
from core.controllers.User.project_controller import (
    UserProjectListView,
    UserProjectDetailView
)
from core.controllers.User.task_controller import (
    UserTaskListView,
    UserTaskDetailView
)
from django.utils.decorators import decorator_from_middleware
from core.middleware.user_auth import UserAuthMiddleware

user_auth_required = decorator_from_middleware(UserAuthMiddleware)

urlpatterns = [
    # Public routes
    path('register/', UserRegisterView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('forgot-password/', UserForgotPasswordView.as_view(), name='user-forgot-password'),
    path('reset-password/', UserResetPasswordView.as_view(), name='user-reset-password'),
    
    # Protected routes
    path('profile/', user_auth_required(UserProfileView.as_view()), name='user-profile'),
    path('change-password/', user_auth_required(UserChangePasswordView.as_view()), name='user-change-password'),

    # Client Management
    path('clients/', user_auth_required(UserClientListView.as_view()), name='user-clients'),
    path('clients/<uuid:client_id>/', user_auth_required(UserClientDetailView.as_view()), name='user-client-detail'),

    # Project Management
    path('projects/', user_auth_required(UserProjectListView.as_view()), name='user-projects'),
    path('projects/<uuid:project_id>/', user_auth_required(UserProjectDetailView.as_view()), name='user-project-detail'),

    # Task Management
    path('tasks/', user_auth_required(UserTaskListView.as_view()), name='user-tasks'),
    path('tasks/<uuid:task_id>/', user_auth_required(UserTaskDetailView.as_view()), name='user-task-detail'),
]
