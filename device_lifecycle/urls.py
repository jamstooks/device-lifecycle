from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic.base import RedirectView, TemplateView

from .apps.dashboard.views import DashboardRedirectView

urlpatterns = [
    url(r'^$', RedirectView.as_view(url='/accounts/login/')),

    # Recruitment
    url(r'^home/$', TemplateView.as_view(
        template_name='recruit/home.html'), name='recruit_home'),
    url(r'^pricing/$', TemplateView.as_view(
        template_name='recruit/pricing.html'), name='recruit_pricing'),
    url(
        r'^join/',
        include(
            'device_lifecycle.apps.subscriptions.urls',
            namespace='join')
    ),
    url(r'^account/', include('djstripe.urls', namespace="djstripe")),

    # The app
    url(
        '^dashboard/$',
        DashboardRedirectView.as_view(),
        name='dashboard_redirect'),
    url(
        r'^dashboard/(?P<org_slug>[\w\-]+)/',
        include(
            'device_lifecycle.apps.dashboard.urls',
            namespace='dashboard')
    ),

    # Accounts
    url(r'^accounts/', include('allauth.urls')),

    # Dev
    url(r'^admin/', admin.site.urls),
    url(r'^.well-known/acme-challenge/', include('acme_challenge.urls')),
]
