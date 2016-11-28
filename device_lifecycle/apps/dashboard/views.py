from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.db.models.functions import TruncYear
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import (
    CreateView, DetailView, ListView, TemplateView, UpdateView)
from django.urls import reverse

from ..devices.models import (
    Device, Warranty, NoteEvent, RepairEvent, TransferEvent, DecommissionEvent)
from ..organizations.models import Person
from .forms import (
    NoteEventForm, RepairEventForm, TransferEventForm, DecommissionEventForm)

from datetime import date, timedelta


class DashboardBaseView(LoginRequiredMixin):
    pass


class Dashboard(DashboardBaseView, TemplateView):
    template_name = 'dashboard/dashboard.html'


class DeviceList(DashboardBaseView, ListView):
    model = Device


class DeviceDetail(DashboardBaseView, DetailView):
    queryset = Device.objects.all()


class DeviceCreate(DashboardBaseView, CreateView):
    """
        @todo - if a device is created without an owner,
        it should be set as spare

        @question - could a machine be a spare but also have an owner?
        if so, I should add a "make spare" event
    """
    model = Device
    fields = [
        'device_type',
        'manufacturer',
        'model',
        'serial',
        'date_purchased',
        'purchase_price',
        'receipt',
        'current_owner'
    ]

    success_url = '/dashboard/'


class DeviceUpdate(DashboardBaseView, UpdateView):
    model = Device
    template_name = 'devices/device_edit.html'
    fields = [
        'manufacturer',
        'model',
        'serial',
        'date_purchased',
        'purchase_price',
        'receipt'
    ]


class PersonList(DashboardBaseView, ListView):
    model = Person


class PersonDetail(DashboardBaseView, DetailView):
    queryset = Person.objects.all()


class PersonCreate(DashboardBaseView, CreateView):
    model = Person
    fields = [
        'name', 'position', 'email', 'is_active'
    ]
    success_url = '/dashboard/people'  # @todo - reverse


class PersonUpdate(DashboardBaseView, UpdateView):
    model = Person
    template_name = 'organizations/person_edit.html'

    fields = [
        'name', 'position', 'email', 'is_active'
    ]


class EventCreateBase(DashboardBaseView, CreateView):

    def get_device(self):
        if not hasattr(self, 'device'):
            self.device = get_object_or_404(Device, pk=self.kwargs['pk'])
        return self.device

    def get_context_data(self, *args, **kwargs):
        _context = super(EventCreateBase, self).get_context_data(
            *args, **kwargs)
        _context['device'] = self.get_device()
        return _context

    def form_valid(self, form):
        # the current device needs to be automatically added to the event
        self.object = form.save(device=self.get_device())
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse(
            'dashboard:device_detail',
            kwargs={'pk': self.object.device.id})


class NoteEventCreate(EventCreateBase):
    model = NoteEvent
    form_class = NoteEventForm
    template_name = 'devices/events/noteevent_form.html'


class RepairEventCreate(EventCreateBase):
    model = RepairEvent
    form_class = RepairEventForm
    template_name = 'devices/events/repairevent_form.html'


class TransferEventCreate(EventCreateBase):
    model = TransferEvent
    form_class = TransferEventForm
    template_name = 'devices/events/repairevent_form.html'

    def form_valid(self, form):

        # both the device and the previous owner are automatically applied
        device = self.get_device()
        self.object = form.save(
            device=device, transferred_from=device.current_owner)

        # after saving, the device's current owner needs to change
        device = self.object.device
        device.current_owner = self.object.transferred_to
        if not self.object.transferred_to:
            device.status = device.STATUS_CHOICES.spare
        else:
            device.status = device.STATUS_CHOICES.active
        device.save()
        return HttpResponseRedirect(self.get_success_url())


class DecommissionEventCreate(EventCreateBase):
    model = DecommissionEvent
    form_class = DecommissionEventForm
    template_name = 'devices/events/decommissionevent_form.html'

    def form_valid(self, form):

        device = self.get_device()
        self.object = form.save(device=device)

        # after saving, the device's current owner needs to change
        self.object.device.status = self.object.device.STATUS_CHOICES.retired
        self.object.device.save()

        return HttpResponseRedirect(self.get_success_url())


class SummaryReport(DashboardBaseView, TemplateView):
    template_name = 'dashboard/reports/summary.html'

    def get_context_data(self, *args, **kwargs):
        _ctx = super(SummaryReport, self).get_context_data(*args, **kwargs)
        _ctx['device_counts'] = Device.objects.exclude(
            status=Device.STATUS_CHOICES.retired).values(
            'device_type').annotate(dcount=Count('device_type'))
        return _ctx


class AgeReport(DashboardBaseView, TemplateView):
    template_name = 'dashboard/reports/age.html'

    def get_context_data(self, *args, **kwargs):
        _ctx = super(AgeReport, self).get_context_data(*args, **kwargs)

        # The x-axis: purchase years
        qs = Device.objects.active()
        qs = qs.order_by('date_purchased')
        qs = qs.filter(date_purchased__isnull=False)
        qs = qs.annotate(year=TruncYear('date_purchased'))
        years = []
        for y in qs.values_list('year', flat=True):
            if y not in years:  # distinct not support locally in sqlite
                years.append(y)
        _ctx['years'] = years

        # The y-axis: counts by device
        max_count = 0
        rows = []
        for _type, label in Device.DEVICE_TYPE_CHOICES:

            qs = Device.objects.active().filter(date_purchased__isnull=False)
            qs = qs.order_by('date_purchased')
            qs = qs.filter(device_type=_type)

            if qs:
                row = {
                    'label': label,
                    'values': [0 for i in range(len(_ctx['years']))]
                }
                # we have to have 0 values when the year doesn't exist
                row['values'] = [0 for i in range(len(_ctx['years']))]

                qs = qs.annotate(year=TruncYear('date_purchased'))
                qs = qs.values('year').annotate(ycount=Count('year'))

                for d in qs:
                    row['values'][years.index(d['year'])] += d['ycount']
                    if max(row['values']) > max_count:
                        max_count = max(row['values'])

                rows.append(row)
        _ctx['rows'] = rows
        _ctx['x_axis_vals'] = range(max_count+1)

        return _ctx
