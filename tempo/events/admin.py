from django.contrib import admin

from . import models


@admin.register(models.Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [
        'verbose_name',
        'code',
        'value_type',
        'default_value',
        'creation_date',
    ]

    search_fields = [
        'verbose_name',
        'code',
        'description',
    ]

    readonly_fields = [
        'slug',
    ]


@admin.register(models.EventConfig)
class EventConfigAdmin(admin.ModelAdmin):
    list_display = [
        'event',
        'user',
        'creation_date',
    ]

    search_fields = [
        'event__verbose_name',
        'event__code',
        'event__description',
        'user__username',
    ]

    raw_id_fields = [
        'event',
        'user',
    ]

    list_select_related = [
        'user',
        'event',
    ]


@admin.register(models.Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = [
        'config',
        'value',
        'start',
    ]

    search_fields = [
        'config__event__verbose_name',
        'config__event__code',
        'config__event__description',
    ]

    list_select_related = [
        'config__user',
        'config__event',
    ]

    raw_id_fields = [
        'config',
    ]
