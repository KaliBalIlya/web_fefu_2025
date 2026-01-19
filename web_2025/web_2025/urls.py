"""
web_2025/web_2025/urls.py
URL configuration for web_2025 project.
"""
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse


def healthz(request):
    return HttpResponse("ok")


urlpatterns = [
    path('healthz', healthz),           # ← ВАЖНО: healthcheck
    path('admin/', admin.site.urls),
    path('', include('fefu_lab.urls')),
]

handler404 = 'fefu_lab.views.page_not_found'
