from django.forms import ModelForm
from django.forms import modelform_factory

from ..devices.models import (
    PurchaseEvent, NoteEvent, RepairEvent,
    TransferEvent, DecommissionEvent, Warranty)


class DeviceChildForm(ModelForm):
    """
    Use modelforms to extend this
    """
    def save(self, device, commit=True):
        self.instance.device = device
        return super(DeviceChildForm, self).save(commit)


class WarrantyForm(DeviceChildForm):
    class Meta:
        model = Warranty
        fields = [
            'start_date', 'end_date', 'description', 'link', 'documentation']


class PurchaseEventForm(DeviceChildForm):
    class Meta:
        model = PurchaseEvent
        fields = [
            'date', 'vendor_name', 'vendor_address',
            'vendor_website', 'purchase_price', 'receipt']

    def save(self, device, commit=True):
        self.instance.purchased_device = device
        return super(PurchaseEventForm, self).save(device, commit)


class NoteEventForm(DeviceChildForm):
    class Meta:
        model = NoteEvent
        fields = ['date', 'notes']


class RepairEventForm(DeviceChildForm):
    class Meta:
        model = RepairEvent
        fields = [
            'date', 'cost', 'receipt',
            'vendor_name', 'vendor_address', 'notes']


class DecommissionEventForm(DeviceChildForm):
    class Meta:
        model = DecommissionEvent
        fields = ['date', 'method', 'cost', 'receipt', 'notes']


class TransferEventForm(DeviceChildForm):
    class Meta:
        model = TransferEvent
        fields = ['date', 'transferred_to', 'notes']

    def save(self, device, transferred_from, commit=True):
        self.instance.transferred_from = transferred_from
        return super(TransferEventForm, self).save(device, commit)
