from __future__ import unicode_literals

from django.db import models


class Person(models.Model):

    name = models.CharField(max_length=256)
    email = models.EmailField(blank=True, null=True)
    position = models.CharField(max_length=256)
    is_active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name
