from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from main.models import Keyring


class Command(BaseCommand):
    help = 'Adds a new key to the Keyring table'

    def add_arguments(self, parser):
        parser.add_argument('name', type=str)
        parser.add_argument('key', type=str)

    def handle(self, *args, **kwargs):
        name, key = kwargs['name'],  kwargs['key']

        try:
            Keyring.objects.get(name=name)
            self.stdout.write(self.style.ERROR('Key with this name already exists.'))
        except ObjectDoesNotExist:
            Keyring.objects.create(name=name, key=key)
            self.stdout.write(self.style.SUCCESS('Successfully added key.'))
