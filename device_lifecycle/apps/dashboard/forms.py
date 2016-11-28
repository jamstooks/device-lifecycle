from django.forms import ModelForm
from django.forms import modelform_factory

from ..devices.models import (
    NoteEvent, RepairEvent, TransferEvent, DecommissionEvent)


class BaseEventForm(ModelForm):
    """
    Use modelforms to extend this
    """
    def save(self, device, commit=True):
        self.instance.device = device
        return super(BaseEventForm, self).save(commit)


class NoteEventForm(BaseEventForm):
    class Meta:
        model = NoteEvent
        fields = ['date', 'notes']


class RepairEventForm(BaseEventForm):
    class Meta:
        model = RepairEvent
        fields = [
            'date', 'cost', 'receipt',
            'vendor_name', 'vendor_address', 'notes']


class DecommissionEventForm(BaseEventForm):
    class Meta:
        model = DecommissionEvent
        fields = ['date', 'method', 'cost', 'receipt']


class TransferEventForm(BaseEventForm):
    class Meta:
        model = TransferEvent
        fields = ['date', 'transferred_to']

    def save(self, device, transferred_from, commit=True):
        self.instance.transferred_from = transferred_from
        return super(TransferEventForm, self).save(device, commit)
