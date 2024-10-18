"""
* Commands: Documentation
"""
# Third Party Imports
import click
from omnitils.files import dump_data_file

# Local Imports
from api.apps import HexproofConfig
from api.routes import main_router


@click.command
def docs_openapi() -> None:
    """Generates the `openapi.json` defining our API schema."""
    _schema = main_router.get_openapi_schema()
    dump_data_file(_schema, (HexproofConfig.PATH.BASE / 'openapi.json'))


@click.group(
    commands={
        'openapi': docs_openapi
    },
    invoke_without_command=True,
    context_settings={'ignore_unknown_options': True})
@click.pass_context
def docs_group(ctx: click.Context, force: bool = False):
    """Command group for generating docs files."""
    if ctx.invoked_subcommand is None:
        ctx.invoke(docs_openapi, force=force)
    pass
