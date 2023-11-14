from django.db import models


class Keyring(models.Model):
    name = models.CharField(max_length=255, unique=True)
    key = models.TextField()
    active = models.BooleanField(default=True)
