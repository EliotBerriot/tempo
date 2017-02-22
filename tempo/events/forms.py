from django import forms

from . import models


class TemplateCreateForm(forms.ModelForm):
    class Meta:
        model = models.Template
        fields = (
            'verbose_name',
            'description',
            'value_type',
            'is_public',
            'required_value',
            'default_value',
            'display_template',
        )
