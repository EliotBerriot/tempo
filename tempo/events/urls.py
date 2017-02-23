# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url, include

from . import views

events_patterns = [
    url(
        regex=r'^create$',
        view=views.EventCreate.as_view(),
        name='create'
    ),
]
urlpatterns = [
    url(
        r'^log$',
        view=views.Log.as_view(),
        name='log'
    ),
    url(
        r'^events/',
        include(events_patterns, namespace='events'),
    ),
]
