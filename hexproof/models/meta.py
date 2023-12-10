"""
* Models tracking Resource Metadata
"""
# Third Party Imports
from django.db.models import CharField, DateField, Model, TextChoices, TextField
from django.utils import timezone

# Local Imports
from hexproof.schemas import MetaSchema
from hexproof.utils.project import get_current_version


"""
* Enums
"""


class ResourceTypes(TextChoices):
    """Types of data resources."""
    # MTGJSON resources
    MTGJSON = ('mtgjson', 'MTGJSON')

    # Scryfall resources
    SCRYFALL = ('scryfall', 'Scryfall')

    # Hexproof resources
    SETS = ('sets', 'Sets')
    SYMBOLS = ('symbols', 'Symbols')


"""
* Models
"""


class Meta(Model):
    """Metadata containing details on when data and asset sources have been updated."""

    # Model Fields
    resource = CharField(max_length=255, choices=ResourceTypes.choices)
    date = DateField(default=timezone.now)
    version = CharField(max_length=255, default=get_current_version)
    uri = TextField()

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
        """str: Returns the formatted version string (version+date), e.g. 1.1.0+20240101."""
        return f'{self.version}+{self.date_formatted}'

    """
    * API Objects
    """

    @property
    def _api_obj(self) -> MetaSchema:
        return MetaSchema(
            resource=self.resource,
            version=self.version_formatted,
            date=self.date_displayed,
            uri=self.uri
        )
