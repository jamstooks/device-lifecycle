"""
    Not using this now, but here if we want to display messages
"""

from django.contrib import messages
from django.db.models.functions import TruncYear


def get_device_qs_purchase_years(qs):
    _qs = qs.order_by('purchaseevent__date')
    _qs = qs.filter(purchaseevent__date__isnull=False)
    _qs = qs.annotate(year=TruncYear('purchaseevent__date'))
    years = []
    for y in _qs.values_list('year', flat=True):
        if y and y not in years:  # distinct not support locally in sqlite
            years.append(y)
    return years


class FormMessagingMixin(object):

    def form_valid(self, form):
        messages.add_message(
            self.request, messages.SUCCESS, 'Save successful!')
        return super(FormMessagingMixin, self).form_valid(form)

    def form_invalid(self, form):
        messages.add_message(
            self.request, messages.ERROR, 'Please fix the errors below.')
        return super(FormMessagingMixin, self).form_invalid(form)
