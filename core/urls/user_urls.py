from django.urls import path
from core.controllers.User.auth_controller import UserAuthController

urlpatterns = [
    path('login/', UserAuthController.as_view(), name='user-login'),
]
