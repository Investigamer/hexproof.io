"""
* Signals: Models of type "Symbols"
"""
# Third Party Imports
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

# Local Imports
from hexproof.models import SymbolRarity

"""
* Signals
"""


@receiver(post_save, sender=SymbolRarity)
def clear_cache_on_save(sender, instance, **kwargs):
    """Clear the cache for class method 'get_rarity' on save."""
    sender.get_rarity.cache_clear()


@receiver(post_delete, sender=SymbolRarity)
def clear_cache_on_delete(sender, instance, **kwargs):
    """Clear the cache for class method 'get_rarity' on delete."""
    sender.get_rarity.cache_clear()
