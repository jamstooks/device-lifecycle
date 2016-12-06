from django.contrib import admin

from .models import Person, Settings


class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'is_active')

admin.site.register(Person, PersonAdmin)


class SettingsAdmin(admin.ModelAdmin):
    list_display = ('organization',)

admin.site.register(Settings, SettingsAdmin)
