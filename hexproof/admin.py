# First Party Imports
from django.contrib import admin

# Third Party Imports
from hexproof.models import APIKey, Meta


@admin.register(APIKey)
class KeyringAdmin(admin.ModelAdmin):
    pass


@admin.register(Meta)
class MetaAdmin(admin.ModelAdmin):
    pass
