from django.contrib import admin

from . import models


@admin.register(models.Template)
class TemplateAdmin(admin.ModelAdmin):
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


@admin.register(models.Event)
class TemplateAdmin(admin.ModelAdmin):
    list_display = [
        'template',
        'user',
        'value',
        'time',
    ]

    search_fields = [
        'template__verbose_name',
        'template__code',
        'template__description',
    ]

    list_select_related = [
        'user',
        'template',
    ]
