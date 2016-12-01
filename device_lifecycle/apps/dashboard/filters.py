import django_filters
from django import forms

from ..devices.models import Device
from .utils import get_device_qs_purchase_years


class DeviceFilter(django_filters.FilterSet):
    date_purchased = django_filters.ChoiceFilter(
        label='Year Purchased',
        name='purchaseevent',
        lookup_expr='date__year',
        widget=forms.Select)

    class Meta:
        model = Device
        fields = ['date_purchased']

    def __init__(self, *args, **kwargs):

        super(DeviceFilter, self).__init__(*args, **kwargs)

        years = get_device_qs_purchase_years(kwargs['queryset'])
        year_choices = [(str(y.year), str(y.year)) for y in years]

        self.filters['date_purchased'].extra.update(
            {'choices': [(None, 'All Years')] + year_choices})

        self.filters['date_purchased'].widget = forms.Select(
            attrs={'onchange': 'this.form.submit();'})
