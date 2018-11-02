"""music_stream URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.shortcuts import redirect
from django.http import Http404, HttpResponseNotFound
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from main.views import load_playlist

    
def redirect_404(request):
    ip = get_client_ip(request)
    print(ip)
    #raise Http404("Page not found")
    return HttpResponseNotFound('<h1>Page not found</h1>')

urlpatterns = [
    path(r'', include('main.urls', namespace='main')),
    path(r'\.well-known/', include('letsencrypt.urls')),
    path(r'admin/', admin.site.urls),
    path(r'login/', include('user.urls', namespace='login')),
    path(r'.well-known/', include('letsencrypt.urls')),
] + staticfiles_urlpatterns()
 
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
