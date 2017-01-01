# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-01 00:04
from __future__ import unicode_literals

from django.db import migrations


def set_retired_device(apps, schema_editor):
    DecommissionEvent = apps.get_model("devices", "DecommissionEvent")
    for event in DecommissionEvent.objects.all():
        event.retired_device = event.device
        event.save()


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0005_decommissionevent_retired_device'),
    ]

    operations = [
        migrations.RunPython(set_retired_device),
    ]