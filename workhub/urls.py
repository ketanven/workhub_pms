from django.urls import path, include
from django.http import HttpResponse


urlpatterns = [

    # Health Check
    path('', lambda request: HttpResponse("Welcome to Freelancer Work Management System API"), name='health'),

    path('api/', include('core.urls')),
]

