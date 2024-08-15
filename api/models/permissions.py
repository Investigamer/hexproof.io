"""
* API Data Models
"""
# Third Party Imports
from django.db.models import IntegerChoices, IntegerField, TextField, BooleanField, CharField, Model
from hexproof.hexapi import schema as Hexproof
from ninja import Schema


class APIKey(Model):
    """API access keys."""

    class KeyPermission(IntegerChoices):
        """Determines the permission level of an APIKey."""
        ADMIN = 0
        MODERATOR = 1
        SUPPORTER = 2
        PUBLIC = 3

    # APIKey Fields
    name = CharField(max_length=255, unique=True)
    key = TextField()
    active = BooleanField(default=True)
    permission = IntegerField(
        choices=KeyPermission.choices,
        default=KeyPermission.PUBLIC)

    """
    * Input Schema
    """

    class InputSchema(Schema):
        name: str
        key: str
        active: bool
        permission: 'APIKey.KeyPermission'

    @property
    def _api_obj(self) -> Hexproof.APIKey:
        return Hexproof.APIKey(
            name=self.name,
            key=self.key,
            active=self.active,
            permission=self.permission
        )
