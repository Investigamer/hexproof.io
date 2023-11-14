from ninja import ModelSchema
from .models import Keyring


class KeyringSchema(ModelSchema):
    class Config:
        model = Keyring
        model_fields = ['name', 'key', 'active']
