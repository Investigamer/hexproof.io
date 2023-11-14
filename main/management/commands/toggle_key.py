from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from main.models import Keyring


class Command(BaseCommand):
    help = 'Toggles the active status of a key in the Keyring table'

    def add_arguments(self, parser):
        parser.add_argument('name', type=str)

    def handle(self, *args, **kwargs):
        name = kwargs['name']

        try:
            k = Keyring.objects.get(name=name)
            k.active = bool(not k.active)
            k.save()
            status = self.style.SUCCESS('ENABLED') if k.active else self.style.WARNING('DISABLED')
            self.stdout.write(self.style.SUCCESS(f"Key '{name}' is now {status}."))
        except ObjectDoesNotExist:
            self.stdout.write(self.style.ERROR(f"Key '{name}' does not exist."))
