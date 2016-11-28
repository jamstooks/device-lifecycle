from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic.base import RedirectView

urlpatterns = [
    url(r'^$', RedirectView.as_view(url='/accounts/login/')),
    url(
        r'^dashboard/',
        include(
            'device_lifecycle.apps.dashboard.urls',
            namespace='dashboard')
    ),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^admin/', admin.site.urls),
]