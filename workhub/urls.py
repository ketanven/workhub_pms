from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static
from django.http import FileResponse, Http404
from pathlib import Path


def favicon_view(_request):
    candidates = [
        Path(settings.BASE_DIR) / 'assets' / 'invoice-logo.png',
        Path(settings.BASE_DIR) / 'assets' / 'logo.png',
        Path(settings.BASE_DIR) / 'static' / 'favicon.ico',
        Path(settings.BASE_DIR) / 'static' / 'favicon.png',
    ]
    for icon_path in candidates:
        if icon_path.exists() and icon_path.is_file():
            if icon_path.suffix.lower() == '.ico':
                return FileResponse(open(icon_path, 'rb'), content_type='image/x-icon')
            return FileResponse(open(icon_path, 'rb'), content_type='image/png')
    raise Http404("Favicon not found")


urlpatterns = [

    # Health Check
    path('', lambda request: HttpResponse("Welcome to Freelancer Work Management System API"), name='health'),
    path('favicon.ico', favicon_view, name='favicon'),

    path('api/', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
