from django import forms

from . import models


class EventCreateForm(forms.ModelForm):
    class Meta:
        model = models.Event
        fields = (
            'verbose_name',
            'description',
        )


class EntryCreateForm(forms.ModelForm):
    class Meta:
        model = models.Entry
        fields = (
            'config',
            'comment',
            'detail_url',
            'is_public',
        )
