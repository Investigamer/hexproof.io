"""
* Command: sync_sets
* Pulls the latest Scryfall and MTGJSON bulk 'Set' data and
compiles the unified 'Set' object database tables.
"""
from typing import Union

# Third Party Imports
from django.core.management.base import BaseCommand
from pathlib import Path

# Local Imports

from hexproof.models import Set
from hexproof.models.mtg.sets import add_mtgjson_set_data
from hexproof.models.mtg.symbols import match_symbol_to_set
from hexproof.sources import mtgjson as MTJ
from hexproof.sources import scryfall as SCRY
from hexproof.utils.files import load_data_file


class Command(BaseCommand):
    help = "Rebuilds the 'Set' Model table using latest Set object data."

    def handle(self, *args, **kwargs):
        """Compiles the database table for the 'Set' model."""

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

        # Operation successful
        print("Sets synced!")
