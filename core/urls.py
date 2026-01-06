from django.urls import path

from core.controllers.Admin.auth_controller import AdminAuthController
from core.controllers.User.auth_controller import UserAuthController

urlpatterns = [
    path('admin/login/', AdminAuthController.as_view()),
    path('user/login/', UserAuthController.as_view()),
]
