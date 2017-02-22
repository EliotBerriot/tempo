from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import urlresolvers

from . import forms


class TemplateCreate(LoginRequiredMixin, generic.CreateView):
    form_class = forms.TemplateCreateForm
    template_name = 'events/templates/create.html'
    success_url = urlresolvers.reverse_lazy('home')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        r = super().form_valid(form)
        form.instance.users.add(self.request.user)
        return r
