from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from django.db.models import Count
from django.db.models.functions import TruncYear
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView)
from django.urls import reverse

from ..devices.models import (
    Device, Warranty, EventBase, PurchaseEvent, NoteEvent,
    RepairEvent, TransferEvent, DecommissionEvent)
from .filters import InventoryFilterSet, ReplacementTimelineFilterset
from .forms import (
    DeviceForm, PersonForm, PurchaseEventForm, NoteEventForm, RepairEventForm,
    TransferEventForm, DecommissionEventForm, WarrantyForm)
from ..people.models import Person, Settings
from .utils import get_device_qs_purchase_years

from collections import OrderedDict
from datetime import date, timedelta
from organizations.mixins import MembershipRequiredMixin
from organizations.models import Organization, OrganizationUser


class DashboardRedirectView(LoginRequiredMixin, TemplateView):
    """
    Either displays a list of orgs a user can access
    or redirects them to their only one

    If a user does not have an org, then they will be directed
    to register eventually
    """
    template_name = "dashboard/org_list.html"

    def dispatch(self, request, *args, **kwargs):

        if self.request.user.is_authenticated():
            self.ou_list = OrganizationUser.objects.filter(
                user=self.request.user)
            if not self.ou_list:
                # redirect to registration eventually
                return HttpResponseForbidden()
            if self.ou_list.count() == 1:
                return HttpResponseRedirect(
                    reverse(
                        'dashboard:device_list',
                        kwargs={
                            "org_slug": self.ou_list[0].organization.slug}))

        return super(DashboardRedirectView, self).dispatch(
            request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        _context = super(DashboardRedirectView, self).get_context_data(
            *args, **kwargs)
        org_list = []
        for org_user in self.ou_list:
            org_list.append(org_user.organization)
        _context['organization_list'] = self.org_list
        return _context


class DashboardBaseView(LoginRequiredMixin, MembershipRequiredMixin):
    """
    Currently requires login and
    requires that the user belong to the selected organization

    Adds the current organization to the context
    """
    def get_organization(self):
        if not hasattr(self, 'organization'):
            self.organization = get_object_or_404(
                Organization, slug=self.kwargs['org_slug'])
        return self.organization

    def get_context_data(self, *args, **kwargs):
        _context = super(DashboardBaseView, self).get_context_data(
            *args, **kwargs)
        _context['organization'] = self.get_organization()
        return _context


class ActivityFeedView(DashboardBaseView, ListView):
    model = EventBase
    template_name = 'dashboard/activity_feed.html'

    def get_queryset(self):
        # @todo - consider pagination or filtering
        return self.model.objects.all()[:30]


class DashboardView(DashboardBaseView, TemplateView):
    template_name = 'dashboard/dashboard.html'


class DeviceBaseView(DashboardBaseView):

    def get_queryset(self):
        # @todo - consider pagination or filtering
        org = self.get_organization()
        return org.device_set.all()

    def form_valid(self, form):
        # only used for the form versions, but useful for simplicity
        # the current device needs to be automatically added to the event
        self.object = form.save(organization=self.get_organization())
        return HttpResponseRedirect(self.get_success_url())

    def get_form_kwargs(self):
        kwargs = super(DeviceBaseView, self).get_form_kwargs()
        kwargs['organization'] = self.get_organization()
        return kwargs


class DeviceListView(DeviceBaseView, ListView):

    def get_context_data(self, *args, **kwargs):
        _context = super(DeviceListView, self).get_context_data(
            *args, **kwargs)

        # if there is no get, set an initial filter value
        data = self.request.GET.copy()
        if len(data) == 0:
            data['status'] = Device.STATUS_CHOICES.active

        _context['filter'] = InventoryFilterSet(
            data,
            queryset=self.get_queryset())
        return _context


class DeviceDetailView(DeviceBaseView, DetailView):
    pass


class DeviceCreateView(DeviceBaseView, CreateView):
    """
        @todo - if a device is created without an owner,
        it should be set as spare

        @question - could a machine be a spare but also have an owner?
        if so, I should add a "make spare" event
    """
    model = Device
    form_class = DeviceForm

    def get_success_url(self):
        return reverse(
            'dashboard:device_list',
            kwargs={'org_slug': self.get_organization().slug})


class DeviceUpdateView(DeviceBaseView, UpdateView):
    model = Device
    form_class = DeviceForm
    template_name = 'devices/device_edit.html'


class DeviceDeleteView(DashboardBaseView, DeleteView):
    model = Device

    def get_success_url(self):
        return reverse(
            'dashboard:device_list',
            kwargs={'org_slug': self.get_organization().slug})


class PersonBaseView(DashboardBaseView):

    def get_queryset(self):
        # @todo - consider pagination or filtering
        org = self.get_organization()
        return org.person_set.all()

    def form_valid(self, form):
        # only used for the form versions, but useful for simplicity
        # the current device needs to be automatically added to the event
        self.object = form.save(organization=self.get_organization())
        return HttpResponseRedirect(self.get_success_url())


class PersonList(PersonBaseView, ListView):
    pass


class PersonDetail(PersonBaseView, DetailView):
    pass


class PersonCreate(PersonBaseView, CreateView):
    model = Person
    form_class = PersonForm

    def get_success_url(self):
        return reverse(
            'dashboard:person_list',
            kwargs={'org_slug': self.get_organization().slug})


class PersonUpdate(PersonBaseView, UpdateView):
    model = Person
    form_class = PersonForm
    template_name = 'people/person_edit.html'


class DeviceChildEditMixin(DashboardBaseView):

    def get_device(self):
        if not hasattr(self, 'device'):
            self.device = get_object_or_404(Device, pk=self.kwargs['pk'])
        return self.device

    def get_context_data(self, *args, **kwargs):
        _context = super(DeviceChildEditMixin, self).get_context_data(
            *args, **kwargs)
        _context['device'] = self.get_device()
        if hasattr(self, 'form_title'):
            _context['form_title'] = self.form_title
        _context['delete_url'] = self.get_delete_url()
        return _context

    def form_valid(self, form):

        # the current device needs to be automatically added to the event
        self.object = form.save(device=self.get_device())
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse(
            'dashboard:device_detail',
            kwargs={
                'org_slug': self.get_organization().slug,
                'pk': self.object.device.id})

    def get_object(self, queryset=None):
        # should only be called for edit/delete views
        if not hasattr(self, 'object'):
            d = self.get_device()
            self.object = get_object_or_404(
                self.model.objects.filter(device=d),
                pk=self.kwargs['child_pk'])
        return self.object

    def get_delete_url(self):
        obj = self.get_object()
        if obj:
            return obj.get_delete_url()


class WarrantyBaseView(DeviceChildEditMixin):
    model = Warranty
    form_class = WarrantyForm
    template_name = 'devices/events/device_child_form.html'


class WarrantyCreateView(WarrantyBaseView, CreateView):
    form_title = "Add a Warranty"


class WarrantyUpdateView(WarrantyBaseView, UpdateView):
    form_title = "Edit Warranty"


class WarrantyDeleteView(WarrantyBaseView, DeleteView):
    template_name = 'devices/warranty_confirm_delete.html'

    def get_context_data(self, *args, **kwargs):
        # this insures that only this warranty gets displayed
        _context = super(WarrantyDeleteView, self).get_context_data(
            *args, **kwargs)
        _context['warranty_set'] = [self.get_object()]
        return _context


class PurchaseEventBaseView(DeviceChildEditMixin):
    model = PurchaseEvent
    form_class = PurchaseEventForm
    template_name = 'devices/events/device_child_form.html'


class PurchaseEventCreateView(PurchaseEventBaseView, CreateView):
    form_title = "Add Purchase Details"


class PurchaseEventUpdateView(PurchaseEventBaseView, UpdateView):
    form_title = "Change Purchase Details"


class PurchaseEventDeleteView(PurchaseEventBaseView, DeleteView):
    template_name = 'devices/events/event_confirm_delete.html'


class NoteEventBaseView(DeviceChildEditMixin):
    model = NoteEvent
    form_class = NoteEventForm
    template_name = 'devices/events/device_child_form.html'


class NoteEventCreateView(NoteEventBaseView, CreateView):
    form_title = "Add a Note"


class NoteEventUpdateView(NoteEventBaseView, UpdateView):
    form_title = "Change Note"


class NoteEventDeleteView(NoteEventUpdateView, DeleteView):
    template_name = 'devices/events/event_confirm_delete.html'


class RepairEventBaseView(DeviceChildEditMixin):
    model = RepairEvent
    form_class = RepairEventForm
    template_name = 'devices/events/device_child_form.html'


class RepairEventCreateView(RepairEventBaseView, CreateView):
    form_title = "Add a Repair"


class RepairEventUpdateView(RepairEventBaseView, UpdateView):
    form_title = "Update Repair"


class RepairEventDeleteView(RepairEventBaseView, DeleteView):
    template_name = 'devices/events/event_confirm_delete.html'


class TransferEventBaseView(DeviceChildEditMixin):
    model = TransferEvent
    form_class = TransferEventForm
    template_name = 'devices/events/device_child_form.html'

    def get_form_kwargs(self):
        kwargs = super(TransferEventBaseView, self).get_form_kwargs()
        kwargs['organization'] = self.get_organization()
        return kwargs

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


class TransferEventCreateView(TransferEventBaseView, CreateView):
    form_title = "Transfer this device"


class TransferEventUpdateView(TransferEventBaseView, UpdateView):
    form_title = "Change this transfer"


class TransferEventDeleteView(TransferEventBaseView, DeleteView):
    template_name = 'devices/events/event_confirm_delete.html'


class DecommissionEventBaseView(DeviceChildEditMixin):
    model = DecommissionEvent
    form_class = DecommissionEventForm
    template_name = 'devices/events/device_child_form.html'

    def form_valid(self, form):

        device = self.get_device()
        self.object = form.save(device=device)

        # after saving, the device's current owner and status needs to change
        self.object.device.status = self.object.device.STATUS_CHOICES.retired
        self.object.device.current_owner = None
        self.object.device.save()

        return HttpResponseRedirect(self.get_success_url())


class DecommissionEventCreateView(DecommissionEventBaseView, CreateView):
    form_title = "Decommission this device"


class DecommissionEventUpdateView(DecommissionEventBaseView, UpdateView):
    form_title = "Change this decommission"


class DecommissionEventDeleteView(DecommissionEventBaseView, DeleteView):
    template_name = 'devices/events/event_confirm_delete.html'


class SummaryReport(DashboardBaseView, TemplateView):
    template_name = 'dashboard/reports/summary.html'

    def get_context_data(self, *args, **kwargs):
        _ctx = super(SummaryReport, self).get_context_data(*args, **kwargs)

        qs = self.get_organization().device_set.active()
        qs = qs.values('device_type').annotate(dcount=Count('device_type'))

        _ctx['device_counts'] = qs.order_by()
        return _ctx


class AgeReport(DashboardBaseView, TemplateView):
    template_name = 'dashboard/reports/age.html'

    def get_context_data(self, *args, **kwargs):
        _ctx = super(AgeReport, self).get_context_data(*args, **kwargs)

        # The x-axis: purchase years
        qs = self.get_organization().device_set.active()
        years = get_device_qs_purchase_years(qs)
        _ctx['years'] = years

        # The y-axis: counts by device
        max_count = 0
        rows = []
        for _type, label in Device.DEVICE_TYPE_CHOICES:

            qs = self.get_organization().device_set.active()
            qs = qs.filter(purchaseevent__date__isnull=False)
            qs = qs.order_by('purchaseevent__date')
            qs = qs.filter(device_type=_type)

            if qs:
                row = {
                    'label': label,
                    'values': [0 for i in range(len(years))]
                }
                # we have to have 0 values when the year doesn't exist
                row['values'] = [0 for i in range(len(years))]

                qs = qs.annotate(year=TruncYear('purchaseevent__date'))
                qs = qs.values('year').annotate(ycount=Count('year'))

                for d in qs.order_by():
                    row['values'][years.index(d['year'])] += d['ycount']
                    if max(row['values']) > max_count:
                        max_count = max(row['values'])

                rows.append(row)
        _ctx['rows'] = rows
        _ctx['x_axis_vals'] = range(max_count+1)

        return _ctx


class ReplacementTimelineReport(DeviceBaseView, TemplateView):
    """
    This view shows how many devices will be in their 1st, 2nd, 3rd, etc
    years of their replacement windows for each year.

    If the max start for any device type is 3 (for example),
    show the next 3 years. Let's assume that laptops have a window
    of 3-5 years and desktops have a window of 3-6 years

    Here's an example context:

        chart_data[
            ['x', 2016, 2017, 2018, 2019],
            ['1st year', 2, 1, 2, 4,],
            ['2nd year', 3, 2, 1, 2,],
            ['3rd year', 0, 3, 2, 1,]
        ]

        @assumption - only display one device type at a time
    """

    template_name = 'dashboard/reports/replacement_timeline.html'

    def get_queryset(self):
        return self.get_organization().device_set.filter(
            device_type=self.request.GET['device_type'])

    def get_context_data(self, *args, **kwargs):
        _context = super(ReplacementTimelineReport, self).get_context_data(
            *args, **kwargs)

        settings = self.get_organization().settings
        today = date.today()

        # set up the device_type filter
        data = self.request.GET.copy()
        if len(data) == 0:
            data['device_type'] = Device.DEVICE_TYPE_CHOICES.laptop
            selected_type = Device.DEVICE_TYPE_CHOICES.laptop
        else:
            selected_type = self.request.GET['device_type']

        queryset = self.get_organization().device_set.active().filter(
            device_type=data['device_type'])
        type_filter = ReplacementTimelineFilterset(data, queryset)

        # the years to use are this year + window end years
        # for example if laptop windows are 3-5 years and
        # this year is 2016... then 2016, 2017, 2018, 2019 and 2020
        # will be displayed

        window_start = getattr(settings, "%s_start" % selected_type)
        window_end = getattr(settings, "%s_end" % selected_type)

        year_list = range(today.year - 1, today.year + window_end + 1)

        chart_data = OrderedDict()
        chart_data['years'] = year_list

        """
        {
            'years': [2016, 2017, 2018, 2019],
            '1st year': [2, 1, 2, 4,],
            '2nd year': [3, 2, 1, 2,],
            '3rd year': [0, 3, 2, 1,]
        }
        """

        for offset in range(window_start, window_end+1):
            key = "Year %d" % (offset - window_start + 1)
            # import pdb; pdb.set_trace()
            chart_data[key] = []
            for year in year_list:
                row = chart_data[key].append(
                    type_filter.qs.filter(
                        purchaseevent__date__year=year-offset).count())

        max_y_val = 0  # the most devices for one year for the y axis
        annual_totals = [0 for x in range(len(year_list))]
        index = 0
        from operator import add
        for k, v in chart_data.items():
            if k is not 'years':
                annual_totals = map(add, annual_totals, v)

        _context['y_values'] = range(max(annual_totals) + 1)
        _context['chart_data'] = chart_data
        _context['filter'] = type_filter

        return _context
