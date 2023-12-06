"""
* API Data Models
"""
from django.db import models


class APIKey(models.Model):
    """API access keys."""
    class KeyPermission(models.IntegerChoices):
        """Determines the permission level of an APIKey."""
        ADMIN = 0
        MODERATOR = 1
        SUPPORTER = 2
        PUBLIC = 3

    # APIKey Fields
    name = models.CharField(max_length=255, unique=True)
    key = models.TextField()
    active = models.BooleanField(default=True)
    permission = models.IntegerField(
        choices=KeyPermission.choices,
        default=KeyPermission.PUBLIC)
