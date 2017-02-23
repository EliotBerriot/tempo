import itertools

from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import urlresolvers, paginator
from django import http

from . import forms
from . import models


class Log(LoginRequiredMixin, generic.TemplateView):
    template_name = 'events/log.html'
    paginate_by = 50

    def get_context_data(self):
        context = super().get_context_data()
        entries = models.Entry.objects.filter(
            config__user=self.request.user
        ).order_by('-start')
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
            days.append((k, list(g)))
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
