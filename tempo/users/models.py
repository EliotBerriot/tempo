# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
import pytz


from django.contrib.auth.models import AbstractUser
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.conf import settings


@python_2_unicode_compatible
class User(AbstractUser):

    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = models.CharField(_('Name of User'), blank=True, max_length=255)
    TZ_CHOICES = [(x, x) for x in pytz.common_timezones]
    timezone = models.CharField(
        choices=TZ_CHOICES, default=settings.TIME_ZONE, max_length=100)

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('users:detail', kwargs={'username': self.username})
