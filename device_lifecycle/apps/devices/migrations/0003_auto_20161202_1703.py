# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-02 17:03
from __future__ import unicode_literals

import device_lifecycle.apps.devices.utils
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0002_device_organization'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='device',
            options={'ordering': ['-purchaseevent__date']},
        ),
        migrations.AlterField(
            model_name='decommissionevent',
            name='receipt',
            field=models.FileField(blank=True, null=True, upload_to=device_lifecycle.apps.devices.utils.get_upload_to),
        ),
        migrations.AlterField(
            model_name='device',
            name='serial',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='lossevent',
            name='documentation',
            field=models.FileField(blank=True, null=True, upload_to=device_lifecycle.apps.devices.utils.get_upload_to),
        ),
        migrations.AlterField(
            model_name='purchaseevent',
            name='receipt',
            field=models.FileField(blank=True, null=True, upload_to=device_lifecycle.apps.devices.utils.get_upload_to),
        ),
        migrations.AlterField(
            model_name='repairevent',
            name='receipt',
            field=models.FileField(blank=True, null=True, upload_to=device_lifecycle.apps.devices.utils.get_upload_to),
        ),
        migrations.AlterField(
            model_name='warranty',
            name='documentation',
            field=models.FileField(blank=True, null=True, upload_to=device_lifecycle.apps.devices.utils.get_upload_to),
        ),
    ]
