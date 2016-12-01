from __future__ import unicode_literals

from django.db import models
from django.urls import reverse

from collections import OrderedDict
from model_utils import Choices

from ..people.models import Person
from organizations.models import Organization


class DeviceManager(models.Manager):
    def active(self):
        return self.exclude(status=self.model.STATUS_CHOICES.retired)


class Device(models.Model):

    DEVICE_TYPE_CHOICES = Choices(
        ('laptop', 'Laptop'),
        ('desktop', 'Desktop'),
        ('printer', 'Printer'),
        ('phone', 'Phone'),
        ('monitor', 'Monitor'),
        ('projector', 'Projector'),
        ('tablet', 'Tablet'),
        ('headset', 'Headset'),
        ('hard_drive', 'Hard Drive'),
        ('webcam', 'Web Cam'),
        ('keyboard', 'Keyboard'),
        ('mouse', 'Mouse'),
    )

    STATUS_CHOICES = Choices(
        ('active', 'Active'),
        ('spare', 'Spare'),
        ('retired', 'Retired')
    )

    TYPE_ICONS = {
        'laptop': 'fa fa-laptop',
        'desktop': 'fa fa-desktop',
        'printer': 'fa fa-print',
        'phone': 'fa fa-mobile',
        'monitor': 'fa fa-television',
        'projector': 'fa fa-film',
        'tablet': 'fa fa-tablet',
        'headset': 'fa fa-headphones',
        'hard_drive': 'fa fa-hdd-o',
        'webcam': 'fa fa-camera',
        'keyboard': 'fa fa-keyboard-o',
        'mouse': 'pe-7s-mouse',
    }

    organization = models.ForeignKey(Organization)
    device_type = models.CharField(max_length=16, choices=DEVICE_TYPE_CHOICES)
    manufacturer = models.CharField(max_length=32)
    model = models.CharField(max_length=64)
    serial = models.CharField(max_length=128)
    current_owner = models.ForeignKey(Person, blank=True, null=True)
    status = models.CharField(
        max_length=16, choices=STATUS_CHOICES, default=STATUS_CHOICES.active)
    description = models.TextField(
        blank=True, null=True,
        help_text="Any additional description of the device if necessary")

    objects = DeviceManager()

    # @todo
    # current_location

    @property
    def icon(self):
        return self.TYPE_ICONS[self.device_type]

    def get_absolute_url(self):
        return reverse(
            'dashboard:device_detail',
            kwargs={'org_slug': self.organization.slug, 'pk': self.pk})

    def get_status_class(self):
        return {
            'active': 'success',
            'spare': 'warning',
            'retired': 'danger',
        }[self.status]

    def __unicode__(self):
        return self.model


class Warranty(models.Model):

    device = models.ForeignKey(Device)
    description = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    link = models.URLField(
        blank=True, null=True, help_text="A link to more information.")
    documentation = models.FileField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Warranties"
        ordering = ['-end_date']

    def get_delete_url(self):
        return reverse(
            "dashboard:warranty_delete",
            kwargs={
                'org_slug': self.device.organization.slug,
                'pk': self.device.id,
                'child_pk': self.id})


class EventBase(models.Model):
    """
    An event is anything that can happen to a device.
    This is an abstract base class
    """
    ICON_MAPPINGS = {
        'purchase': 'fa fa-usd',
        'note': 'fa fa-bookmark',
        'repair': 'fa fa-wrench',
        'transfer': 'fa fa-exchange',
        'decommission': 'fa fa-recycle',
        'loss': 'fa fa-exclamation-triangle'
    }

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
        return self.ICON_MAPPINGS[self.event_type]

    def get_delete_url(self):
        # dict-find-by-value action
        short_type_name = EVENT_TYPES.keys()[
            EVENT_TYPES.values().index(self.__class__)]
        return reverse(
            "dashboard:%s_delete" % short_type_name,
            kwargs={
                'org_slug': self.device.organization.slug,
                'pk': self.device.id,
                'child_pk': self.id})


class PurchaseEvent(EventBase):
    """
    Purchase Events are slightly different from other events, because there
    can only be one purchase per device.

    I made this an event instead of creating a separate one-to-one model here
    because I want to be able to include this event when showing all events.

    The `purchase_price` and `receipt` fields come from the device and will be
    displayed in the form, but the `date` field needs to mirror. To do this,
    I've added an additional one-to-one field on this model and ensure that
    every device has only one purchase event and that event can be accessed
    efficiently for display and reports (`select_related()`).

    Events:
        device is created:
            - device form is displayed
            - after save, user is encouraged to record the purchase event

        purchase is created:
            - `PurchaseEvent` is created.
            - "+" menu no longer displays option for adding a purchase
    """
    purchased_device = models.OneToOneField(Device)
    vendor_name = models.CharField(max_length=128, blank=True, null=True)
    vendor_address = models.TextField(blank=True, null=True)
    vendor_website = models.URLField(blank=True, null=True)
    purchase_price = models.FloatField(blank=True, null=True)
    receipt = models.FileField(blank=True, null=True)

    class Meta:
        verbose_name = 'Purchase'


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
EVENT_TYPES['purchase'] = PurchaseEvent
EVENT_TYPES['note'] = NoteEvent
EVENT_TYPES['repair'] = RepairEvent
EVENT_TYPES['transfer'] = TransferEvent
EVENT_TYPES['decommission'] = DecommissionEvent
EVENT_TYPES['loss'] = LossEvent
