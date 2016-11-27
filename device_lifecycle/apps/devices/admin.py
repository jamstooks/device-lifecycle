from django.contrib import admin

from .models import Device, Warranty, NoteEvent


class WarrantyInline(admin.TabularInline):
    model = Warranty
    extra = 1


class EventInline(admin.TabularInline):
    model = NoteEvent
    extra = 1


class DeviceAdmin(admin.ModelAdmin):
    inlines = (WarrantyInline, EventInline)
    list_display = ('current_owner', 'manufacturer', 'model', 'serial')

admin.site.register(Device, DeviceAdmin)
