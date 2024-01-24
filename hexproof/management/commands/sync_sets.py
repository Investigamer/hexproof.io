"""
* Command: sync_sets
* Pulls the latest Scryfall and MTGJSON bulk 'Set' data and
compiles the unified 'Set' object database tables.
"""
# Local Imports
from datetime import datetime
from typing import Union

# Third Party Imports
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from pathlib import Path

# Local Imports
from hexproof.apps import HexproofConfig
from hexproof.models import Set, Meta
from hexproof.models.mtg.sets import add_mtgjson_set_data
from hexproof.models.mtg.symbols import match_symbol_to_set
from hexproof.sources import mtgjson as MTJ
from hexproof.sources import scryfall as SCRY
from hexproof.utils.files import load_data_file
from hexproof.utils.project import get_current_version


class Command(BaseCommand):
    help = "Rebuilds the 'Set' Model table using latest Set object data."

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true')
        parser.add_argument('--force', action='store_true')

    def handle(self, *args, **options):
        """Compiles the database table for the 'Set' model."""

        # Clear table if 'clear' arg was passed
        if options.get('clear'):
            Set.objects.all().delete()

        # Check current metadata to see if sets are up-to-date
        JSON_meta: MTJ.Meta = MTJ.get_meta()
        try:
            mtgjson_resource = Meta.objects.get(resource='mtgjson')
        except ObjectDoesNotExist:
            mtgjson_resource = Meta.objects.create(resource='mtgjson', uri=str(MTJ.MTJ_URL.API_META))
        if mtgjson_resource.version_formatted == JSON_meta.get('version'):
            # Process the commend anyway if 'force' arg was passed
            if not options.get('force'):
                print("MTGJSON data already up-to-date!")
                return

        # Pull the latest Scryfall and MTGJSON data
        JSON_data: dict[str, MTJ.SetList] = {d['code']: d for d in MTJ.get_set_list()}
        SCRY_data: dict[str, SCRY.Set] = {d['code']: d for d in SCRY.get_set_list()}
        sets_path: Path = MTJ.get_sets_all()

        # Add the Scryfall data
        # TODO: Create a unified Set type
        data: list[dict] = [
            {
                'block': d.get('block', JSON_data.get(code, {}).get('block')),
                'block_code': d.get('block_code'),
                'code': code,
                'code_alt': JSON_data.get(code, {}).get('codeV3'),
                'code_arena': d.get('arena_code'),
                'code_keyrune': JSON_data.get(code, {}).get('keyruneCode'),
                'code_mtgo': d.get('mtgo_code', JSON_data.get(code, {}).get('mtgoCode')),
                'code_parent': d.get('parent_set_code', JSON_data.get(code, {}).get('parentCode')),
                'count_cards': d.get('card_count'),
                'count_printed': d.get('printed_size', JSON_data.get(code, {}).get('totalSetSize')),
                'date_released': d.get('released_at', JSON_data.get(code, {}).get('releaseDate')),
                'id_oracle': d.get('id'),
                'id_cardmarket': JSON_data.get(code, {}).get('mcmId'),
                'id_cardmarket_extras': JSON_data.get(code, {}).get('mcmIdExtras'),
                'id_tcgplayer': d.get('tcgplayer_id'),
                'is_foil_only': d.get('foil_only'),
                'is_nonfoil_only': d.get('nonfoil_only'),
                'is_digital_only': d.get('digital'),
                'is_foreign_only': JSON_data.get(code, {}).get('isForeignOnly'),
                'is_paper_only': JSON_data.get(code, {}).get('isPaperOnly'),
                'is_preview': JSON_data.get(code, {}).get('isPartialPreview'),
                'name': d.get('name'),
                'name_cardmarket': JSON_data.get(code, {}).get('mcmName'),
                'scryfall_icon_uri': ''.join(d.get('icon_svg_uri').split('?')[:-1]),
                'type': d.get('set_type')
            } for code, d in SCRY_data.items()
        ]

        # Set data post-processing
        for d in data:

            # Add deeper MTGJSON 'Set' data
            set_path = (sets_path / d['code'].upper()).with_suffix('.json')
            try:
                set_data: Union[MTJ.Set, dict] = load_data_file(set_path).get('data', {})
            except (FileNotFoundError, ValueError, OSError):
                set_data = {}
            add_mtgjson_set_data(d, set_data)

            # Add expansion symbol code
            d['symbol'] = match_symbol_to_set(d)

        # Update the database
        for set_obj in data:

            # Remove null values
            set_obj = {k: v for k, v in set_obj.items() if v not in [None, '']}

            # Check for an existing Set
            if query := Set.objects.filter(code=set_obj['code']):
                query.update(**set_obj)
                continue

            # Add new Set
            Set.objects.create(**set_obj)

        # Update MTGJSON metadata
        try:
            obj = Meta.objects.get(resource='mtgjson')
            obj.date = JSON_meta.get('date', '')
            obj.version = ''.join(JSON_meta.get('version', '').split('+')[:-1])
            obj.uri = str(MTJ.MTJ_URL.API_META)
            obj.save()
        except ObjectDoesNotExist:
            print("Meta for resource 'mtgjson' not found!")

        # Update Scryfall metadata
        try:
            obj = Meta.objects.get(resource='scryfall')
            obj.date = datetime.now()
            obj.version = get_current_version()
            obj.uri = str(SCRY.SCRY_URL.API_BULK)
            obj.save()
        except ObjectDoesNotExist:
            print("Meta for resource 'scryfall' not found!")

        # Update 'sets' resource metadata
        try:
            obj = Meta.objects.get(resource='sets')
            obj.date = datetime.now()
            obj.version = get_current_version()
            obj.uri = str(HexproofConfig.API_URL / 'sets')
            obj.save()
        except ObjectDoesNotExist:
            print("Meta for resource 'sets' not found!")

        # Operation successful
        print("Sets synced!")
