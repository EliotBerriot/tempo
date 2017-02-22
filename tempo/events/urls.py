# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url, include

from . import views

templates_patterns = [
    url(
        regex=r'^create$',
        view=views.TemplateCreate.as_view(),
        name='create'
    ),
]
urlpatterns = [
    url(
        r'^templates/',
        include(templates_patterns, namespace='templates'),
    ),
]
