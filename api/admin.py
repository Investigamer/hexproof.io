# First Party Imports
from django.contrib import admin

# Third Party Imports
from api.models import permissions as Permissions
from api.models import meta as Meta
from api.models import sets as Sets
from api.models import symbols as Symbols

"""
* Permission Models
"""


@admin.register(Permissions.APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ['name', 'active', 'permission']


"""
* Metadata Models
"""


@admin.register(Meta.Meta)
class MetaAdmin(admin.ModelAdmin):
    list_display = ['resource', 'version_formatted', 'uri']


"""
* Set Models
"""


@admin.register(Sets.Set)
class SetAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'type']


"""
* Symbol Models
"""


@admin.register(Symbols.SymbolSet)
class SymbolSetAdmin(admin.ModelAdmin):
    list_display = ['code', 'supported']


@admin.register(Symbols.SymbolWatermark)
class SymbolWatermarkAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_parent_code']

    @admin.display(description='Parent Code', ordering='parent_set_code__code')
    def get_parent_code(self, obj: Symbols.SymbolWatermark) -> str:
        return obj.parent_symbol_set.code
