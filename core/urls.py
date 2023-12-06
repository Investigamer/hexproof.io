"""
* URL Route Config

* The `urlpatterns` list routes URLs to views or 'endpoints'. For more information, see
https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""
# Third Party Imports
from django.contrib import admin
from django.urls import path, include

# App-wide URL routing
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('hexproof.routes'))
]
