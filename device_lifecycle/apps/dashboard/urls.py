from django.conf.urls import url

from .views import (
    ActivityFeedView,
    DashboardView,
    DeviceCreateView,
    DeviceDeleteView,
    DeviceDetailView,
    DeviceListView,
    DeviceListExcelView,
    DeviceUpdateView,
    PersonList,
    PersonDetail,
    PersonCreate,
    PersonUpdate,
    WarrantyCreateView,
    WarrantyUpdateView,
    WarrantyDeleteView,
    PurchaseEventCreateView,
    PurchaseEventUpdateView,
    PurchaseEventDeleteView,
    NoteEventCreateView,
    NoteEventUpdateView,
    NoteEventDeleteView,
    RepairEventCreateView,
    RepairEventUpdateView,
    RepairEventDeleteView,
    TransferEventCreateView,
    TransferEventUpdateView,
    TransferEventDeleteView,
    DecommissionEventCreateView,
    DecommissionEventUpdateView,
    DecommissionEventDeleteView,
    SummaryReport,
    AgeReport,
    ReplacementTimelineReport)

urlpatterns = [

    # devices
    # url(r'^$', Dashboard.as_view(), name='dashboard'),
    url(r'^$', DeviceListView.as_view(), name='device_list'),
    url(
        r'^export/$',
        DeviceListExcelView.as_view(),
        name='device_list_export'),
    url(r'^activity/$', ActivityFeedView.as_view(), name='activity_feed'),
    url(r'^devices/add/$', DeviceCreateView.as_view(), name='device_add'),
    url(
        r'^devices/(?P<pk>[\w\-]+)/$',
        DeviceDetailView.as_view(),
        name='device_detail'),
    url(
        r'^devices/(?P<pk>[\w\-]+)/edit/$',
        DeviceUpdateView.as_view(),
        name='device_update'),
    url(
        r'^devices/(?P<pk>[\w\-]+)/delete/$',
        DeviceDeleteView.as_view(),
        name='device_delete'),
    url(
        r'^devices/(?P<pk>[\w\-]+)/warranty/add/$',
        WarrantyCreateView.as_view(),
        name='warranty_add'),
    url(
        r'^devices/(?P<pk>[\w\-]+)/warranty/(?P<child_pk>[\w\-]+)/$',
        WarrantyUpdateView.as_view(),
        name='warranty_edit'),
    url(
        r'^devices/(?P<pk>[\w\-]+)/warranty/(?P<child_pk>[\w\-]+)/delete/$',
        WarrantyDeleteView.as_view(),
        name='warranty_delete'),
    url(
        r'^devices/(?P<pk>[\w\-]+)/purchase/add/$',
        PurchaseEventCreateView.as_view(),
        name='purchase_add'),
    url(
        r'^devices/(?P<pk>[\w\-]+)/purchase/(?P<child_pk>[\w\-]+)/$',
        PurchaseEventUpdateView.as_view(),
        name='purchase_edit'),
    url(
        r'^devices/(?P<pk>[\w\-]+)/purchase/(?P<child_pk>[\w\-]+)/del/$',
        PurchaseEventDeleteView.as_view(),
        name='purchase_delete'),
    url(
        r'^devices/(?P<pk>[\w\-]+)/note/add/$',
        NoteEventCreateView.as_view(),
        name='note_add'),
    url(
        r'^devices/(?P<pk>[\w\-]+)/note/(?P<child_pk>[\w\-]+)/$',
        NoteEventUpdateView.as_view(),
        name='note_edit'),
    url(
        r'^devices/(?P<pk>[\w\-]+)/note/(?P<child_pk>[\w\-]+)/del/$',
        NoteEventDeleteView.as_view(),
        name='note_delete'),
    url(
        r'^devices/(?P<pk>[\w\-]+)/repair/add/$',
        RepairEventCreateView.as_view(),
        name='repair_add'),
    url(
        r'^devices/(?P<pk>[\w\-]+)/repair/(?P<child_pk>[\w\-]+)/$',
        RepairEventUpdateView.as_view(),
        name='repair_edit'),
    url(
        r'^devices/(?P<pk>[\w\-]+)/repair/(?P<child_pk>[\w\-]+)/del/$',
        RepairEventDeleteView.as_view(),
        name='repair_delete'),
    url(
        r'^devices/(?P<pk>[\w\-]+)/transfer/add/$',
        TransferEventCreateView.as_view(),
        name='transfer_add'),
    url(
        r'^devices/(?P<pk>[\w\-]+)/transfer/(?P<child_pk>[\w\-]+)/$',
        TransferEventUpdateView.as_view(),
        name='transfer_edit'),
    url(
        r'^devices/(?P<pk>[\w\-]+)/transfer/(?P<child_pk>[\w\-]+)/del/$',
        TransferEventDeleteView.as_view(),
        name='transfer_delete'),
    url(
        r'^devices/(?P<pk>[\w\-]+)/decommission/add/$',
        DecommissionEventCreateView.as_view(),
        name='decommission_add'),
    url(
        r'^devices/(?P<pk>[\w\-]+)/decommission/(?P<child_pk>[\w\-]+)/$',
        DecommissionEventUpdateView.as_view(),
        name='decommission_edit'),
    url(
        r'^devices/(?P<pk>[\w\-]+)/decommission/(?P<child_pk>[\w\-]+)/del/$',
        DecommissionEventDeleteView.as_view(),
        name='decommission_delete'),


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
    url(
        r'^reports/timeline/$',
        ReplacementTimelineReport.as_view(),
        name='replacement_timeline'),
]
