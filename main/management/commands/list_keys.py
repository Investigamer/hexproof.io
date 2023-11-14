from django.core.management.base import BaseCommand
from main.models import Keyring


class Command(BaseCommand):
    help = 'Lists all keys in the Keyring table'

    def handle(self, *args, **kwargs):
        keys = [k for k in Keyring.objects.all()]
        if not keys:
            self.stdout.write(self.style.SUCCESS('No keys found!'))
            return
        for k in keys:
            status = self.style.SUCCESS('True') if k.active else self.style.WARNING('False')
            self.stdout.write(f"{self.style.SUCCESS(k.name)} | {k.key} | {status}")
