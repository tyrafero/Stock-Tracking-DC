"""stockmgtr URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from .views import ReactAppView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),  # API endpoints
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # In development, you might want to keep the Django views
    urlpatterns += [path('', include('stock.urls'))]
else:
    # In production, serve React app for all other routes
    # Exclude static files, assets, media, admin, and API from catch-all
    urlpatterns += [
        re_path(r'^(?!static|assets|media|admin|api).*$', ReactAppView.as_view(), name='react-app'),
    ]
