"""
* Command Group: Update Data and File Resources
"""
import os
import shutil
from concurrent.futures import ThreadPoolExecutor

# Third Party Imports
import click
from hexproof.mtgjson import fetch as MJsonFetch
from hexproof.mtgjson import schema as MJson
from hexproof.mtgjson.enums import MTGJsonURL
from hexproof.scryfall import fetch as ScryFetch
from hexproof.scryfall.enums import ScryURL
from hexproof.vectors import fetch as VectorsFetch
from omnitils.files import load_data_file

# Local Imports
from api.apps import HexproofConfig
from api.models.meta import create_or_update_meta, Meta

"""
* Shared Arguments
"""

ARG_FORCED_OPTIONAL = click.option(
    '-F', '--force',
    is_flag=True,
    default=False,
    show_default=True,
    help="Update data even if version metadata hasn't changed.")

"""
* Commands: Update -> MTGJSON
"""


@click.command
@ARG_FORCED_OPTIONAL
def update_mtgjson_all(force: bool = False) -> None:
    """Updates all MTGJSON resources and 'Meta' object."""

    # Grab the latest MTGJSON 'Meta' object
    try:
        _meta_path = MJsonFetch.cache_meta(HexproofConfig.PATH.MTGJSON_META)
        _meta_obj = load_data_file(_meta_path).get('data', {})
        _meta = MJson.Meta(**_meta_obj)
    except Exception as e:
        # Unable to load 'Meta' object
        HexproofConfig.logger.exception(e)
        return HexproofConfig.logger.warning("Unable to load MTGJSON 'Meta' object!")

    # Skip further updates if data is current
    if not force and Meta.get_version('mtgjson') == _meta.version:
        return HexproofConfig.logger.info("Already using latest data from source 'MTGJSON'!")

    # List MTGJSON datasets to update
    scheduled = [
        (MJsonFetch.cache_set_list, {'path': HexproofConfig.PATH.MTGJSON_SET_LIST}),
        (MJsonFetch.cache_decks_all, {'path': HexproofConfig.PATH.MTGJSON, 'remove': True}),
        (MJsonFetch.cache_sets_all, {'path': HexproofConfig.PATH.MTGJSON, 'remove': True}),
    ]

    # Run each job
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as runner:
        tasks = [runner.submit(func, **kw) for func, kw in scheduled]
        [n.result() for n in tasks]

    # Save new MTGJSON 'Meta'
    create_or_update_meta(
        resource='mtgjson',
        uri=str(MTGJsonURL.BulkJSON.Meta),
        version=''.join(_meta.version.split('+')[:-1]),
        date=_meta.date)
    HexproofConfig.logger.info('MTGJSON data updated!')


"""
* Commands: Update -> Scryfall
"""


@click.command
@ARG_FORCED_OPTIONAL
def update_scryfall_all(force: bool = False) -> None:
    """Updates all Scryfall resources and 'Meta' object."""

    # Check if Scryfall needs an update
    _current = Meta.get_version('scryfall')
    _latest = Meta.get_app_version_formatted()
    if not force and _current == _latest:
        return HexproofConfig.logger.info("Already using latest data from source 'Scryfall'!")

    # List Scryfall datasets to update
    scheduled = [
        (ScryFetch.cache_set_list, {'path': HexproofConfig.PATH.SCRYFALL_SET_LIST}),
    ]

    # Run each job
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as runner:
        tasks = [runner.submit(func, **kw) for func, kw in scheduled]
        [n.result() for n in tasks]

    # Update Scryfall meta
    create_or_update_meta(
        resource='scryfall',
        uri=str(ScryURL.API.Bulk.All))
    HexproofConfig.logger.info('Scryfall data updated!')


"""
* Commands: Update -> MTG-Vectors
"""


@click.command
@ARG_FORCED_OPTIONAL
def update_vectors_all(force: bool = False) -> None:
    """Updates all MTG-Vectors resources and 'Meta' object."""

    # Grab the latest MTG-Vectors 'Meta' object
    try:
        packages = VectorsFetch.get_latest_release(
            owner_repo=HexproofConfig.URLS.VECTORS_REPO,
            auth_token=HexproofConfig.AUTH_GITHUB) or {}
        optimized = packages.get('optimized')
        if optimized is None:
            return HexproofConfig.logger.warning(
                "Unable to find an optimized package in latest MTG-Vectors release!")
    except Exception as e:
        # Unable to load 'Meta' object
        HexproofConfig.logger.error(e)
        return HexproofConfig.logger.warning("Unable to load MTG-Vectors 'Meta' object!")

    # Check if mtg-vectors needs an update
    if not force and Meta.get_version('mtg-vectors[optimized]') == optimized.version:
        return HexproofConfig.logger.info("MTG-Vectors: No updates found!")
    HexproofConfig.logger.info(f'Updates found: MTG-Vectors -> {optimized.version}')

    # Update local mtg-vectors assets
    _path = HexproofConfig.PATH.VECTORS
    HexproofConfig.logger.info(f'Downloading package: {optimized.uri}')
    if _path.is_dir():
        try:
            shutil.rmtree(_path)
        except PermissionError as e:
            HexproofConfig.logger.exception(e)
            return HexproofConfig.logger.error(
                'Unable to remove previous mtg-vectors cache! '
                'Check directory permissions.')
    VectorsFetch.cache_vectors_package(
        directory=_path, url=optimized.uri)

    # Update mtg-vectors metadata
    for name, _meta in packages.items():
        create_or_update_meta(
            resource=f'mtg-vectors[{name}]',
            uri=_meta.uri,
            version=_meta.version.split('+')[0],
            date=_meta.date)
        HexproofConfig.logger.opt(colors=True).success(
            f'Updated metadata: <bold>mtg-vectors[{name}]</bold> -> {_meta.version}')
    HexproofConfig.logger.success('MTG-Vectors catalog and metadata updated!')


"""
* Commands: Shorthand
"""


@click.command
@ARG_FORCED_OPTIONAL
@click.pass_context
def update_all(ctx: click.Context, force: bool = False) -> None:
    """Executes every update command in series."""
    ctx.invoke(update_mtgjson_all, force=force)
    ctx.invoke(update_scryfall_all, force=force)
    ctx.invoke(update_vectors_all, force=force)


"""
* Command Groups
"""


@click.group(
    commands={'.': update_mtgjson_all},
    invoke_without_command=True,
    context_settings={'ignore_unknown_options': True}
)
@ARG_FORCED_OPTIONAL
@click.pass_context
def update_mtgjson_group(ctx: click.Context, force: bool = False):
    """Command group for performing updates to MTGJSON sourced resources and datasets."""
    if ctx.invoked_subcommand is None:
        ctx.invoke(update_mtgjson_all, force=force)
    pass


@click.group(
    commands={'.': update_scryfall_all},
    invoke_without_command=True,
    context_settings={'ignore_unknown_options': True}
)
@ARG_FORCED_OPTIONAL
@click.pass_context
def update_scryfall_group(ctx: click.Context, force: bool = False):
    """Command group for performing updates to Scryfall sourced resources and datasets."""
    if ctx.invoked_subcommand is None:
        ctx.invoke(update_scryfall_all, force=force)
    pass


@click.group(
    commands={'.': update_vectors_all},
    invoke_without_command=True,
    context_settings={'ignore_unknown_options': True}
)
@ARG_FORCED_OPTIONAL
@click.pass_context
def update_vectors_group(ctx: click.Context, force: bool = False):
    """Command group for performing updates to MTG-Vectors repository resources and datasets."""
    if ctx.invoked_subcommand is None:
        print(0)
        ctx.invoke(update_vectors_all, force=force)
    pass


@click.group(
    commands={
        '.': update_all,
        'mtgjson': update_mtgjson_group,
        'scryfall': update_scryfall_group,
        'vectors': update_vectors_group
    },
    invoke_without_command=True,
    context_settings={'ignore_unknown_options': True}
)
@ARG_FORCED_OPTIONAL
@click.pass_context
def update_group(ctx: click.Context, force: bool = False):
    """Command group for performing updates to local resources and datasets."""
    if ctx.invoked_subcommand is None:
        ctx.invoke(update_all, force=force)
    pass
