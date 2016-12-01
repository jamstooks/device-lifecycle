from django.contrib import admin

from .models import Person


class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'is_active')

admin.site.register(Person, PersonAdmin)
