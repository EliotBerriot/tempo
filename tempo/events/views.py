import itertools

from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import urlresolvers, paginator
from django import http
from django.db.models import Q

from taggit.models import Tag

from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import detail_route, list_route

from . import forms
from . import models
from . import serializers


class Log(LoginRequiredMixin, generic.TemplateView):
    template_name = 'events/log.html'
    paginate_by = 50

    def get_context_data(self):
        context = super().get_context_data()
        entries = models.Entry.objects.filter(
            config__user=self.request.user
        ).prefetch_related(
            'tags').order_by('-start').select_related('config__event').with_score()
        p = paginator.Paginator(entries, self.paginate_by)
        try:
            page = int(self.request.GET.get('page', 1))
        except TypeError:
            page = 1
        try:
            page = p.page(page)
        except paginator.EmptyPage:
            raise http.Http404
        days = []
        for k, g in itertools.groupby(
                page.object_list, lambda e: e.start.date()):
            d = {
                'entries': list(g),
            }
            d['score'] = sum([e.get_score() for e in d['entries']])
            d['count'] = len(d['entries'])
            days.append((k, d))
        context['days'] = days
        context['paginator'] = p
        context['is_paginated'] = p.num_pages > 1
        context['page_obj'] = page
        return context


class EventCreate(LoginRequiredMixin, generic.CreateView):
    form_class = forms.EventCreateForm
    template_name = 'events/events/create.html'
    success_url = urlresolvers.reverse_lazy('home')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        r = super().form_valid(form)
        form.instance.configs.create(
            user=self.request.user)
        return r


class EntryCreate(LoginRequiredMixin, generic.TemplateView):
    template_name = 'events/entries/create.html'

    def get_context_data(self):
        context = super().get_context_data()
        context['Entry'] = models.Entry
        return context


class Search(APIView):

    config = {
        'config': {
            'qs': models.EventConfig.objects.select_related('event'),
            'user_attr': 'user',
            'search_fields': ['event__verbose_name'],
            'title_field': 'title',
        }
    }

    def get(self, request, format=None):
        t = request.GET['type']
        query = request.GET['q']
        results = self.get_results(request, t, query)
        return Response({'results': self.serialize_results(results)})

    def get_results(self, request, t, query):
        conf = self.config[t]
        lookups = {
            '{}'.format(conf['user_attr']): request.user,
        }
        q = None
        for f in conf['search_fields']:
            _q = Q(**{'{}__icontains'.format(f): query})
            if not q:
                q = _q
            else:
                q |= _q

        return conf['qs'].filter(**lookups).filter(q)

    def serialize_results(self, qs):
        return [
            {'value': i.pk, 'name': i.title, 'text': i.title}
            for i in qs
        ]


class EntryViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.EntrySerializer

    def get_queryset(self):
        return models.Entry.objects.filter(
            config__user=self.request.user
        )


class TagViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = serializers.TagSerializer

    def get_queryset(self):
        return Tag.objects.all()

    @list_route(methods=['get'])
    def search(self, request, pk=None):
        qs = self.get_queryset().filter(
            slug__icontains=request.GET.get('q', ''))
        serializer = self.serializer_class(qs, many=True)
        return Response({"results": serializer.data},
                        status=200)


class ConfigViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ConfigSerializer

    def get_queryset(self):
        return self.request.user.event_configs.all()

    def create(self, request, *args, **kwargs):
        serializer = serializers.EventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        event = serializer.instance
        event.created_by = request.user
        event.save()

        config = models.EventConfig.objects.create(
            event=event,
            user=request.user
        )
        serializer = self.get_serializer(instance=config)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
