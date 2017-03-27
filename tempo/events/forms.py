import datetime
from django import forms
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

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


class ByDayForm(forms.Form):
    start = forms.DateField(required=False)
    end = forms.DateField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start')
        end = cleaned_data.get('end')
        if not start and not end:
            cleaned_data['end'] = timezone.now().date()
            cleaned_data['start'] = cleaned_data['end'] - datetime.timedelta(days=15)
        try:
            if cleaned_data['start'] >= cleaned_data['end']:
                raise forms.ValidationError('End must be greater than start')
        except (KeyError, TypeError):
            pass


class EntrySuggestionForm(forms.Form):
    date = forms.DateTimeField(required=False)


class StatsForm(forms.Form):
    start = forms.DateField(required=False)
    end = forms.DateField(required=False)
    fill = forms.BooleanField(required=False)

    ORDERING_CHOICES = [
        ('date', _('Ascending')),
        ('-date', _('Descending')),
    ]
    ordering = forms.ChoiceField(choices=ORDERING_CHOICES, required=False)

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start')
        end = cleaned_data.get('end')
        if not start and not end:
            cleaned_data['end'] = timezone.now().date()
            cleaned_data['start'] = cleaned_data['end'] - datetime.timedelta(days=15)
        try:
            if cleaned_data['start'] >= cleaned_data['end']:
                raise forms.ValidationError('End must be greater than start')
        except (KeyError, TypeError):
            pass
