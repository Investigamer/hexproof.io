"""
* Models tracking Resource Metadata
"""
# Standard Library Imports
import datetime
from typing import Optional

# Third Party Imports
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import CharField, DateField, Model, TextField
from django.utils import timezone
from hexproof.providers.hexapi import schema as Hexproof
from ninja import Schema

# Local Imports
from api.apps import HexproofConfig


"""
* Models
"""


class Meta(Model):
    """Metadata containing details on when data and asset sources have been updated."""

    # Model Fields
    resource = CharField(max_length=255, unique=True)
    date = DateField(default=timezone.now)
    version = CharField(max_length=255, default=HexproofConfig.get_current_version)
    uri = TextField()

    """
    * Input Schema
    """

    class InputSchema(Schema):
        resource: str
        date: str | datetime.date | datetime.datetime
        version: str
        uri: str

    """
    * Class Methods
    """

    @classmethod
    def get_version(cls, resource: str) -> Optional[str]:
        """Gets the current version of a given 'Meta' resource.

        Args:
            resource: Resource to get the version of.

        Returns:
            Formatted version of the given resource if found, otherwise None.
        """
        try:
            return cls.objects.get(resource=resource).version_formatted
        except (ObjectDoesNotExist, AttributeError):
            return

    """
    * Formatted Properties
    """

    @property
    def date_displayed(self) -> str:
        """str: Returns the date formatted for display to the user."""
        return self.date.strftime('%Y-%m-%d')

    @property
    def date_formatted(self) -> str:
        """str: Returns the date formatted for use in version strings."""
        return self.date.strftime('%Y%m%d')

    @property
    def resource_formatted(self) -> str:
        """str: Format resource name for use in a URI."""
        return self.resource.replace('_', '/')

    @property
    def version_formatted(self) -> str:
        """str: Returns the formatted version string used for comparison (version+date), e.g. 1.1.0+20240101."""
        return f'{self.version}+{self.date_formatted}'

    """
    * API Objects
    """

    @property
    def _api_obj(self) -> Hexproof.Meta:
        return Hexproof.Meta(
            resource=self.resource,
            version=self.version_formatted,
            date=self.date_displayed,
            uri=self.uri
        )

    """
    * Utility Methods
    """

    @staticmethod
    def get_app_version_formatted() -> str:
        """Gets the current Hexproof API version formatted with date string."""
        _version = HexproofConfig.get_current_version()
        _date = timezone.now().strftime('%Y%m%d')
        return f'{_version}+{_date}'


"""
* Utility Funcs
"""


def create_or_update_meta(
    resource: str,
    uri=str,
    version: Optional[str] = None,
    date: Optional[str | datetime.date | datetime.datetime] = None
) -> None:
    """Creates a new 'Meta' object or updates an existing one.

    Args:
        resource: Name of the API resource.
        uri: URI of the API resource.
        version: Version string of the API resource.
        date: Date API resource was last updated.
    """
    if date is None:
        date = timezone.now()
    if version is None:
        version = HexproofConfig.get_current_version()

    # Update existing 'Meta' object, or create new
    if query := Meta.objects.filter(resource=resource):
        query.update(
            date=date, version=version, uri=uri)
    else:
        Meta.objects.create(
            resource=resource, date=date, version=version, uri=uri)
