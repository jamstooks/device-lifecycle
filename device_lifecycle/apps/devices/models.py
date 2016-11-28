from __future__ import unicode_literals

from django.db import models
from django.urls import reverse

from collections import OrderedDict
from model_utils import Choices

from ..organizations.models import Person


class DeviceManager(models.Manager):
    def active(self):
        return self.exclude(status=self.model.STATUS_CHOICES.retired)


class Device(models.Model):

    DEVICE_TYPE_CHOICES = Choices(
        ('laptop', 'Laptop'),
        ('printer', 'Printer'),
        ('phone', 'Phone'),
        ('monitor', 'Monitor'),
        ('projector', 'Projector'),
        ('tablet', 'Tablet'),
        ('headset', 'Headset'),
        ('hard_drive', 'Hard Drive'),
        ('webcam', 'Web Cam'),
        ('keyboard', 'Keyboard'),
    )

    STATUS_CHOICES = Choices(
        ('active', 'Active'),
        ('spare', 'Spare'),
        ('retired', 'Retired')
    )

    TYPE_ICONS = {
        'laptop': 'laptop',
        'desktop': 'desktop_mac',
        'printer': 'print',
        'phone': 'phone_iphone',
        'monitor': 'tv',
        'projector': 'cast',
        'tablet': 'tablet_android',
        'headset': 'headset_mic',
        'hard_drive': 'storage',
        'webcam': 'linked_camera',
        'keyboard': 'keyboard',
    }

    device_type = models.CharField(max_length=16, choices=DEVICE_TYPE_CHOICES)
    manufacturer = models.CharField(max_length=32)
    model = models.CharField(max_length=64)
    serial = models.CharField(max_length=128)
    date_purchased = models.DateField(blank=True, null=True)
    purchase_price = models.FloatField(blank=True, null=True)
    receipt = models.FileField(blank=True, null=True)
    current_owner = models.ForeignKey(Person, blank=True, null=True)
    status = models.CharField(
        max_length=16, choices=STATUS_CHOICES, default=STATUS_CHOICES.active)

    objects = DeviceManager()

    # @todo
    # current_location

    def get_status_chip_style(self):
        styles = {
            'active': 'mdl-color--green mdl-color-text--white',
            'spare': 'mdl-color--amber mdl-color-text--white',
            'retired': 'mdl-color--red mdl-color-text--white'
        }
        return styles[self.status]

    def get_icon(self):
        return self.TYPE_ICONS[self.device_type]

    def get_absolute_url(self):
        return reverse(
            'dashboard:device_detail',
            kwargs={'pk': self.pk})

    def __unicode__(self):
        return self.model


class Warranty(models.Model):

    device = models.ForeignKey(Device)
    description = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    link = models.URLField(
        blank=True, null=True, help_text="A link to more information.")
    notes = models.TextField(blank=True, null=True)
    documentation = models.FileField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Warranties"


class EventBase(models.Model):
    """
    An event is anything that can happen to a device.
    This is an abstract base class
    """
    event_type = models.CharField(max_length=40)
    device = models.ForeignKey(Device, related_name='events')
    date = models.DateField()
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-date']

    def save(self, *args, **kwargs):
        self.event_type = EVENT_TYPES.keys()[
            EVENT_TYPES.values().index(self.__class__)]
        return super(EventBase, self).save(*args, **kwargs)

    @property
    def instance_type(self):
        """
        The `verbose_name` of the attached event type subclass of this
        main event type object.
        """
        return EVENT_TYPES[self.event_type]._meta.verbose_name

    @property
    def icon(self):
        mapping = {
            'note': 'bookmark',
            'repair': 'build',
            'transfer': 'swap_horiz',
            'decommission': 'cancel',
            'loss': 'warning'
        }
        return mapping[self.event_type]


class NoteEvent(EventBase):
    """
    Just a basic note, no additional information
    """
    class Meta:
        verbose_name = 'Note'


class TransferEvent(EventBase):
    transferred_from = models.ForeignKey(
        Person, blank=True, null=True, related_name="transfered_from",
        help_text="""
        Leave blank if this came from the spare inventory.
        """)
    transferred_to = models.ForeignKey(
        Person, blank=True, null=True, related_name="transfered_to",
        help_text="""
        Leave blank if leaving as a spare.
        """)

    class Meta:
        verbose_name = 'Transfer'


class RepairEvent(EventBase):
    cost = models.FloatField()
    receipt = models.FileField(blank=True, null=True)
    vendor_name = models.CharField(max_length=128)
    vendor_address = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Repair'


class DecommissionEvent(EventBase):
    METHOD_CHOICES = Choices(
        ('recycled', 'Recycled'),
        ('sold', 'Sold'),
        ('disposal service', 'Disposal Service'),
    )
    method = models.CharField(max_length=16, choices=METHOD_CHOICES)
    receipt = models.FileField(blank=True, null=True)
    cost = models.FloatField(
        help_text="""
        Use positive values when selling, negative if paying a service.
        """)

    class Meta:
        verbose_name = 'Decommission'


class LossEvent(EventBase):
    documentation = models.FileField(blank=True, null=True)
    recovery_date = models.DateField(blank=True, null=True)

    class Meta:
        verbose_name = 'Loss'


#  @todo - wait for postgis
# class LocationEvent(EventBase):
#     previous_location
#     new_location

EVENT_TYPES = OrderedDict()
EVENT_TYPES['note'] = NoteEvent
EVENT_TYPES['repair'] = RepairEvent
EVENT_TYPES['transfer'] = TransferEvent
EVENT_TYPES['decommission'] = DecommissionEvent
EVENT_TYPES['loss'] = LossEvent
