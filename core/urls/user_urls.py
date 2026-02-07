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
]
