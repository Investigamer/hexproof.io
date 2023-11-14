from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from main.models import Keyring


class Command(BaseCommand):
    help = 'Deletes a key from the Keyring table'

    def add_arguments(self, parser):
        parser.add_argument('name', type=str)

    def handle(self, *args, **kwargs):
        name = kwargs['name']

        try:
            k = Keyring.objects.get(name=name)
            confirm = input('Are you sure you want to delete this key? (y/n): ')
            if confirm.lower() != 'y':
                self.stdout.write(self.style.WARNING('Deletion cancelled.'))
                return
            k.delete()
            self.stdout.write(self.style.SUCCESS('Successfully deleted key.'))
        except ObjectDoesNotExist:
            self.stdout.write(self.style.ERROR('Key with this name does not exist.'))
