# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-01 00:03
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0003_settings'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='person',
            options={'ordering': ['name'], 'verbose_name_plural': 'People'},
        ),
        migrations.AlterModelOptions(
            name='settings',
            options={'verbose_name_plural': 'Settings'},
        ),
    ]
