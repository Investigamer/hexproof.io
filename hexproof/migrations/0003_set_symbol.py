# Generated by Django 4.2.7 on 2023-12-06 02:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hexproof', '0002_symbol_rarities'),
    ]

    operations = [
        migrations.AddField(
            model_name='set',
            name='symbol',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='hexproof.symbolcollectionset'),
        ),
    ]
