"""
* Command: sync_symbols
* Pulls the latest manifest files from the 'mtg-vectors' repository,
compiles the 'Symbol' object database tables, and updates local symbol assets.
"""
# Standard Library Imports
from pprint import pprint

# Third Party Imports
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from requests import RequestException
import yarl


# Local Imports
from hexproof.models import Meta
from hexproof.apps import HexproofConfig
from hexproof.models.mtg.symbols import (
    add_or_update_symbol_rarities,
    add_or_update_symbol_sets,
    add_or_update_symbol_watermarks,
    add_or_update_symbol_watermark_parents)
from hexproof.sources.vectors.fetch import (
    update_manifest_symbols_set,
    update_package_symbols_set)


class Command(BaseCommand):
    help = "Rebuilds the 'SymbolCollectionSet' database and set symbol asset collection using the latest manifest."

    def handle(self, *args, **kwargs):
        """Compiles the database table for the 'SymbolCollectionSet' model and updates local set symbol assets."""
        # TODO: Add optional args to drop entire symbol table and insert from scratch

        # Update our existing manifest, return if update is unsuccessful or unnecessary
        check, manifest = update_manifest_symbols_set()
        if not check:
            pprint(manifest)
            return

        # Download the zip file
        try:
            update_package_symbols_set(
                yarl.URL(manifest.get('meta', {}).get('uri')))
        except RequestException:
            pprint({'object': 'error', 'message': 'Unable to download latest set symbol package!', 'status': 502})
            return

        # Update rarities
        rarities = manifest.get('set', {}).get('rarities', {})
        add_or_update_symbol_rarities(rarities)

        # Initial symbol collection
        collection = {code: (supported, None) for code, supported in manifest.get('set', {}).get('symbols').items()}
        collection.update({
            # Add alias symbols
            code: (collection[parent][0], parent)
            for code, parent in manifest.get('set', {}).get('routes', {}).items()
            if parent in collection and code not in collection})

        # Add collection and aliases to database
        add_or_update_symbol_sets(collection)

        # Add watermarks and watermarks with parents to database
        add_or_update_symbol_watermarks(manifest.get('watermark', {}).get('symbols', []))
        add_or_update_symbol_watermark_parents()

        # Update metadata
        meta = manifest.get('meta', {})
        try:
            obj = Meta.objects.get(resource='symbols')
            obj.date = meta.get('date', '')
            obj.version = ''.join(meta.get('version', '').split('+')[:-1])
            obj.uri = str(HexproofConfig.API_URL / 'symbols')
            obj.save()
        except ObjectDoesNotExist:
            print("Meta for resource 'symbols' not found!")

        # Operation successful
        print("Symbols synced successfully!")
