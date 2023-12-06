# First Party Imports
from django.contrib import admin

# Third Party Imports
from hexproof.models import APIKey


@admin.register(APIKey)
class KeyringAdmin(admin.ModelAdmin):
    pass
