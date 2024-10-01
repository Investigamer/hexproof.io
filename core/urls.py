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

# Local Imports
from api.routes import main_router

# App-wide URL routing
urlpatterns = [

    # Known static files
    path("favicon.ico", RedirectView.as_view(url=static("favicon.ico"))),

    # Administration page
    path('admin/', admin.site.urls),

    # REST API routes
    path('', main_router.urls)
]
