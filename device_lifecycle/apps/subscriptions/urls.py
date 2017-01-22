from django.conf.urls import url

from .views import SubscribeView, SuccessView

urlpatterns = [
    url(r'^subscribe/$', SubscribeView.as_view(), name='subscribe'),
    url(r'^thank-you/$', SuccessView.as_view(), name='thank_you'),
]
