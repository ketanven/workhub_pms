from django.urls import path, include

urlpatterns = [
    path('admin/', include('core.urls.admin_urls')),
    path('user/', include('core.urls.user_urls')),
]
