from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic.base import RedirectView, TemplateView

from .apps.dashboard.views import DashboardRedirectView

urlpatterns = [
    url(r'^$', RedirectView.as_view(url='/accounts/login/')),
    url(r'^home/$', TemplateView.as_view(template_name='recruit.html')),
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
    url(r'^accounts/', include('allauth.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^.well-known/acme-challenge/', include('acme_challenge.urls')),
]
