from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from main.models import Keyring


class Command(BaseCommand):
    help = 'Updates a key in the Keyring table'

    def add_arguments(self, parser):
        parser.add_argument('name', type=str)
        parser.add_argument('key', type=str)

    def handle(self, *args, **kwargs):
        name = kwargs['name']
        key = kwargs['key']

        try:
            k = Keyring.objects.get(name=name)
            k.key = key
            k.save()
            self.stdout.write(self.style.SUCCESS('Successfully updated key.'))
        except ObjectDoesNotExist:
            self.stdout.write(self.style.ERROR('Key with this name does not exist.'))
