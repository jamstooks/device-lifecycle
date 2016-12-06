from __future__ import unicode_literals

from django.db import models
from django.urls import reverse

from organizations.models import Organization


class Person(models.Model):

    organization = models.ForeignKey(Organization)
    name = models.CharField(max_length=256)
    email = models.EmailField(blank=True, null=True)
    position = models.CharField(max_length=256)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = "People"

    def get_absolute_url(self):
        return reverse(
            'dashboard:person_detail',
            kwargs={'org_slug': self.organization.slug, 'pk': self.pk})

    def __unicode__(self):
        return self.name


class Settings(models.Model):
    DEVICE_TYPE_CHOICES = ('laptop', 'desktop')

    organization = models.OneToOneField(Organization)

    # replacement timeline settings
    laptop_start = models.IntegerField(default=3)
    laptop_end = models.IntegerField(default=5)
    desktop_start = models.IntegerField(default=3)
    desktop_end = models.IntegerField(default=5)

    class Meta:
        verbose_name_plural = "Settings"
