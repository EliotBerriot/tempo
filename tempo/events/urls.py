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
entries_patterns = [
    url(
        regex=r'^create$',
        view=views.EntryCreate.as_view(),
        name='create'
    ),
]
urlpatterns = [
    url(
        r'^timeline$',
        view=views.Log.as_view(),
        name='timeline'
    ),
    url(
        r'^events/',
        include(events_patterns, namespace='events'),
    ),
    url(
        r'^entries/',
        include(entries_patterns, namespace='entries'),
    ),
]
