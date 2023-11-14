"""
* URL Route Config

* The `urlpatterns` list routes URLs to views. For more information, see
https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path

from main.api import api as main_api

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", main_api.urls)
]
