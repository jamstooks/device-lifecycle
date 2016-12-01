"""
    Not using this now, but here if we want to display messages
"""

from django.contrib import messages


class FormMessagingMixin(object):

    def form_valid(self, form):
        messages.add_message(
            self.request, messages.SUCCESS, 'Save successful!')
        return super(FormMessagingMixin, self).form_valid(form)

    def form_invalid(self, form):
        messages.add_message(
            self.request, messages.ERROR, 'Please fix the errors below.')
        return super(FormMessagingMixin, self).form_invalid(form)
