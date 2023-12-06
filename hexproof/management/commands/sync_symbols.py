"""
* Command: sync_symbols
* Pulls the latest manifest files from the 'mtg-vectors' repository,
compiles the 'Symbol' object database tables, and updates local symbol assets.
"""

# Third Party Imports
from django.core.management.base import BaseCommand
from requests import RequestException
import yarl

# Local Imports
from hexproof.models import SymbolRarity, SymbolCollectionSet
from hexproof.sources.vectors.fetch import update_manifest_symbols_set, update_package_symbols_set


class Command(BaseCommand):
    help = "Rebuilds the 'SymbolCollectionSet' database and set symbol asset collection using the latest manifest."

    def handle(self, *args, **kwargs):
        """Compiles the database table for the 'SymbolCollectionSet' model and updates local set symbol assets."""

        # Update our existing manifest, return if update is unsuccessful or unnecessary
        check, manifest = update_manifest_symbols_set()
        if not check:
            return manifest

        # Download the zip file
        try:
            update_package_symbols_set(
                yarl.URL(manifest.get('meta', {}).get('uri')))
        except RequestException:
            return {'object': 'error', 'message': 'Unable to download latest set symbol package!', 'status': 502}

        # Drop all entries from the set symbols database
        SymbolCollectionSet.objects.all().delete()

        # Initial symbol collection
        collection = manifest.get('symbols', {})

        # Create alias collection
        aliases = manifest.get('meta', {}).get('routes', {})
        collection_aliases = {}
        for code, parent in aliases.items():
            if parent in collection and code not in collection:
                collection_aliases[code] = (parent, collection[parent].copy())

        # Add collection to database
        for code, supported in collection.items():
            rarities = SymbolRarity.objects.filter(code__in=supported)
            item = SymbolCollectionSet.objects.create(code=code)
            item.supported.set(rarities)
            item.save()

        # Add alias collection to database
        for code, data in collection_aliases.items():
            parent, supported = data
            rarities = SymbolRarity.objects.filter(code__in=supported)
            item = SymbolCollectionSet.objects.create(code=code, parent=parent)
            item.supported.set(rarities)
            item.save()

        # Operation successful
        print("Symbols synced successfully!")