"""
* URL Route Config

* The `urlpatterns` list routes URLs to views or 'endpoints'. For more information, see
https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""
# Third Party Imports
from django.contrib import admin
from django.templatetags.static import static
from django.urls import path
from django.views.generic import RedirectView

from api.routes import APIRouter

# App-wide URL routing
urlpatterns = [
    path("favicon.ico", RedirectView.as_view(url=static("favicon.ico"))),
    path('admin/', admin.site.urls),
    path('', APIRouter.urls)
]
