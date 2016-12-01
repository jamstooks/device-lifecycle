from __future__ import unicode_literals

from django.db import models
from django.urls import reverse


class Person(models.Model):

    name = models.CharField(max_length=256)
    email = models.EmailField(blank=True, null=True)
    position = models.CharField(max_length=256)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def get_absolute_url(self):
        return reverse(
            'dashboard:person_detail',
            kwargs={'pk': self.pk})

    def __unicode__(self):
        return self.name
