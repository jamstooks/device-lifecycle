import django_filters
from django import forms

from ..devices.models import Device
from ..people.models import Settings
from .utils import get_device_qs_purchase_years


class InventoryFilterSet(django_filters.FilterSet):
    date_purchased = django_filters.ChoiceFilter(
        label='Year Purchased',
        name='purchaseevent',
        lookup_expr='date__year')

    device_type = django_filters.ChoiceFilter(label='Type')

    status = django_filters.ChoiceFilter(label='Status')

    class Meta:
        model = Device
        fields = ['date_purchased', 'device_type', 'status']

    def __init__(self, *args, **kwargs):

        super(InventoryFilterSet, self).__init__(*args, **kwargs)

        # date purchased
        years = get_device_qs_purchase_years(kwargs['queryset'])
        year_choices = [(str(y.year), str(y.year)) for y in years]

        self.filters['date_purchased'].extra.update(
            {'choices': [(None, 'All Years')] + year_choices})

        self.filters['date_purchased'].widget = forms.Select(
            attrs={'onchange': 'this.form.submit();'})

        # device_type
        _types = kwargs['queryset'].values_list(
            'device_type', flat=True).distinct().order_by('device_type')
        _type_choices = [(t, t) for t in _types]

        self.filters['device_type'].extra.update(
            {'choices': [(None, 'All Types')] + _type_choices})

        self.filters['device_type'].widget = forms.Select(
            attrs={'onchange': 'this.form.submit();'})

        # status
        self.filters['status'].extra.update(
            {'choices': [(None, 'All')] + Device.STATUS_CHOICES})

        self.filters['status'].widget = forms.Select(
            attrs={'onchange': 'this.form.submit();'})


class ReplacementTimelineFilterset(django_filters.FilterSet):
    device_type = django_filters.ChoiceFilter(label='Type')

    class Meta:
        model = Device
        fields = ['device_type']

    def __init__(self, *args, **kwargs):

        super(ReplacementTimelineFilterset, self).__init__(*args, **kwargs)

        # device_type
        self.filters['device_type'].extra.update(
            {
                'choices':
                    [(t, t) for t in Settings.DEVICE_TYPE_CHOICES]})

        self.filters['device_type'].widget = forms.Select(
            attrs={'onchange': 'this.form.submit();'})
