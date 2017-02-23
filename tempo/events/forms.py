from django import forms

from . import models


class EventCreateForm(forms.ModelForm):
    class Meta:
        model = models.Event
        fields = (
            'verbose_name',
            'description',
            'value_type',
            'is_public',
            'required_value',
            'default_value',
            'display_template',
        )
