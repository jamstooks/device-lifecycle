from django.forms import ModelForm, ChoiceField

from ..devices.models import (
    Device, Person, PurchaseEvent, NoteEvent, RepairEvent,
    TransferEvent, DecommissionEvent, Warranty)


class DeviceForm(ModelForm):
    class Meta:
        model = Device
        fields = [
            'status',
            'device_type',
            'manufacturer',
            'model',
            'serial',
            'current_owner',
            'description',
        ]

    def __init__(self, organization, *args, **kwargs):
        # limit the current owner choices
        super(DeviceForm, self).__init__(*args, **kwargs)
        self.fields['current_owner'].queryset = organization.person_set.all()

    def save(self, organization, commit=True):
        self.instance.organization = organization
        return super(DeviceForm, self).save(commit)


class PersonForm(ModelForm):
    class Meta:
        model = Person
        fields = ['name', 'position', 'email', 'is_active']

    def save(self, organization, commit=True):
        self.instance.organization = organization
        return super(PersonForm, self).save(commit)


class DeviceChildForm(ModelForm):
    """
    Use modelforms to extend this
    """
    def __init__(self, *args, **kwargs):
        super(DeviceChildForm, self).__init__(*args, **kwargs)
        self.fields['date'].widget.attrs['class'] = 'datepicker'

    def save(self, device, commit=True):
        self.instance.device = device
        return super(DeviceChildForm, self).save(commit)


class WarrantyForm(DeviceChildForm):
    class Meta:
        model = Warranty
        fields = [
            'start_date', 'end_date', 'description', 'link', 'documentation']

    def __init__(self, *args, **kwargs):
        super(DeviceChildForm, self).__init__(*args, **kwargs)
        self.fields['start_date'].widget.attrs['class'] = 'datepicker'
        self.fields['end_date'].widget.attrs['class'] = 'datepicker'


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

    def __init__(self, organization, *args, **kwargs):
        # limit the current owner choices
        super(TransferEventForm, self).__init__(*args, **kwargs)
        self.fields['transferred_to'].queryset = organization.person_set.all()

    def save(self, device, transferred_from, commit=True):
        if not hasattr(self.instance, 'id'):
            # only update the transferred from when created
            self.instance.transferred_from = transferred_from
        return super(TransferEventForm, self).save(device, commit)
