"""
* Command Group: Sync Database
"""
# Local Imports
from concurrent.futures import ThreadPoolExecutor, Future
import os

# Third Party Imports
import click
from hexproof.mtgjson import schema as MJson
from hexproof.scryfall import schema as Scry
from hexproof.vectors import schema as Vectors
from omnitils.files import load_data_file, dump_data_file

# Local Imports
from api.models.meta import create_or_update_meta
from api.apps import HexproofConfig
from api.models import Set
from api.models.symbols import (
    add_or_update_symbol_sets,
    add_or_update_symbol_watermarks)

"""
* Sync Set Model
"""


@click.command
@click.option('--clear-data', '-C', is_flag=True, default=False)
def sync_sets(clear_data: bool = False):
    """Compiles the database table for the 'Set' model."""

    # Clear table if 'clear' arg was passed
    if clear_data:
        Set.objects.all().delete()

    # Get current MTGJSON data
    # Todo: Isolate the elements we need from each dataset and load it piecemeal to avoid memory overhead
    mtgjson_data: dict[str, MJson.SetList] = {
        n['code'].lower(): MJson.SetList(**n) for n in load_data_file(
            path=HexproofConfig.PATH.MTGJSON_SET_LIST).get('data', [])}

    # Get current Scryfall data
    scryfall_data: list[Scry.Set] = [
        Scry.Set(**n) for n in load_data_file(
            HexproofConfig.PATH.SCRYFALL_SET_LIST
        ).get('data', [])]

    # Schedule a job for processing each set
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as pool:
        scheduled: list[Future] = []
        for scry_data in scryfall_data:
            scheduled.append(
                pool.submit(
                    Set.create_or_update,
                    scryfall=scry_data,
                    mtgjson=mtgjson_data.get(scry_data.code)
                ))

        # Wait for scheduled jobs to finish
        [n.result() for n in scheduled]

    # Cache bulk set data
    path = HexproofConfig.PATH.CACHE / 'sets.json'
    data = {d.code: d._api_obj.model_dump() for d in Set.objects.all()}
    dump_data_file(data, path)

    # Update metadata
    create_or_update_meta(
        resource='sets',
        uri=str(HexproofConfig.API_SETS))

    # Operation successful
    HexproofConfig.logger.info("'Set' data synced successfully!")


"""
* Sync Symbol Models
"""


@click.command(
    help="Rebuilds the 'SymbolSet' database and set symbol asset collection using the latest manifest."
)
def sync_symbols():
    """Compiles the database table for the 'SymbolSet' model and updates local set symbol assets."""

    # Get data
    manifest = Vectors.Manifest(
        **load_data_file(HexproofConfig.PATH.VECTORS_MANIFEST))

    # Initial symbol collection
    HexproofConfig.logger.info('Compiling symbol collection ...')
    collection: dict[str, Vectors.SetSymbolMap] = {
        code: Vectors.SetSymbolMap(
            rarities=supported,
            children=[]
        ) for code, supported in manifest.set.symbols.items()
    }

    # Add alias symbols
    for code, code_parent in manifest.set.aliases.items():
        if code_parent in collection and code not in collection:
            collection[code_parent].children.append(code)

    # Add set symbols to database
    HexproofConfig.logger.info("Updating database: 'SymbolSet' ...")
    add_or_update_symbol_sets(
        data=collection)

    # Add watermarks to database
    HexproofConfig.logger.info("Updating database: 'SymbolWatermark' ...")
    add_or_update_symbol_watermarks(
        watermarks=manifest.watermark.symbols)

    # Update metadata
    HexproofConfig.logger.info('Updating resource metadata ...')
    create_or_update_meta(
        resource='symbols',
        uri=str(HexproofConfig.API_SYMBOLS))

    # Operation successful
    HexproofConfig.logger.info("Symbol data synced successfully!")


"""
* Command Groups
"""


@click.group(
    commands=dict(
        sets=sync_sets,
        symbols=sync_symbols
    )
)
def sync_group():
    pass
