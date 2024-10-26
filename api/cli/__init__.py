"""
* CLI Application
"""
# Local Imports
import os

# Third Party Imports
import click
import django

# Instantiate Django settings
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "core.settings")
django.setup()

# Local Imports
from api.apps import HexproofConfig
from api.cli.docs import docs_group
from api.cli.update import update_group
from api.cli.sync import sync_group


""""
* Commands
"""


@click.command
def check_version() -> None:
    """Print the current Hexproof API version."""
    version = HexproofConfig.get_current_version()
    HexproofConfig.logger.info(f'Hexproof API v{version}')


"""
* Command Groups
"""


@click.group(
    commands={
        '--version': check_version,
        'docs': docs_group,
        'sync': sync_group,
        'update': update_group
    },
    invoke_without_command=True,
    context_settings={'ignore_unknown_options': True}
)
@click.pass_context
def cli_application(ctx: click.Context):
    """Hexproof API CLI application entrypoint."""
    if ctx.invoked_subcommand is None:
        ctx.invoke(update_group)
    pass


# Export CLI Application
HexproofCLI = cli_application()
__all__ = ['HexproofCLI']
