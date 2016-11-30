from django.conf.urls import url

from .views import (
    Dashboard,
    DeviceCreate,
    DeviceDetail,
    DeviceList,
    DeviceUpdate,
    PersonList,
    PersonDetail,
    PersonCreate,
    PersonUpdate,
    WarrantyCreateView,
    WarrantyEditView,
    NoteEventCreate,
    RepairEventCreate,
    TransferEventCreate,
    DecommissionEventCreate,
    SummaryReport,
    AgeReport)

urlpatterns = [

    # devices
    # url(r'^$', Dashboard.as_view(), name='dashboard'),
    url(r'^$', DeviceList.as_view(), name='device_list'),
    url(r'^devices/add/$', DeviceCreate.as_view(), name='device_add'),
    url(
        r'^devices/(?P<pk>[\w\-]+)/$',
        DeviceDetail.as_view(),
        name='device_detail'),
    url(
        r'^devices/(?P<pk>[\w\-]+)/edit/$',
        DeviceUpdate.as_view(),
        name='device_update'),
    url(
        r'^devices/(?P<pk>[\w\-]+)/warranty/add/$',
        WarrantyCreateView.as_view(),
        name='warranty_add'),
    url(
        r'^devices/(?P<pk>[\w\-]+)/warranty/(?P<wpk>[\w\-]+)/$',
        WarrantyEditView.as_view(),
        name='warranty_edit'),
    url(
        r'^devices/(?P<pk>[\w\-]+)/note/add/$',
        NoteEventCreate.as_view(),
        name='note_add'),
    url(
        r'^devices/(?P<pk>[\w\-]+)/repair/add/$',
        RepairEventCreate.as_view(),
        name='repair_add'),
    url(
        r'^devices/(?P<pk>[\w\-]+)/transfer/add/$',
        TransferEventCreate.as_view(),
        name='transfer_add'),
    url(
        r'^devices/(?P<pk>[\w\-]+)/decommission/add/$',
        DecommissionEventCreate.as_view(),
        name='decommission_add'),


    # people
    url(r'^people/$', PersonList.as_view(), name='person_list'),
    url(r'^people/add/$', PersonCreate.as_view(), name='person_add'),
    url(
        r'^people/(?P<pk>[\w\-]+)/$',
        PersonDetail.as_view(),
        name='person_detail'),
    url(
        r'^people/(?P<pk>[\w\-]+)/edit/$',
        PersonUpdate.as_view(),
        name='person_update'),

    # reports
    url(r'^reports/$', SummaryReport.as_view(), name='reports_summary'),
    url(r'^reports/ages/$', AgeReport.as_view(), name='reports_age'),
]
