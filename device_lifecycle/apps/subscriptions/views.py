from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.views.generic import FormView, TemplateView

from .forms import StripeForm
import stripe


class CustomerMixin(object):
    def get_customer(self):
        try:
            return self.request.user.customer
        except:
            return Customer.create(request.user)


class StripeMixin(object):
    def get_context_data(self, **kwargs):
        _context = super(StripeMixin, self).get_context_data(**kwargs)
        _context['publishable_key'] = settings.STRIPE_PUBLIC_KEY
        return _context


class SubscribeView(CustomerMixin, StripeMixin, FormView):
    template_name = "subscriptions/subscribe.html"
    form_class = StripeForm
    success_url = reverse_lazy("subscriptions:thank_you")

    def form_valid(self, form):
        customer = self.get_customer()
        customer.update_card(form.cleaned_data.get('stripe_token', None))
        customer.subscribe('basic')
        return super(SubscribeView, self).form_valid(form)


class SuccessView(TemplateView):
    template_name = "subscriptions/thank_you.html"
