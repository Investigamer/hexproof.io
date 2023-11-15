# First Party Imports
from django.contrib import admin

# Third Party Imports
from main.models import Keyring


@admin.register(Keyring)
class KeyringAdmin(admin.ModelAdmin):
    pass
