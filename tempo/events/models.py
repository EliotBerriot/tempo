import uuid
import slugify
import re
import itertools
import datetime
import collections

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver

from taggit.managers import TaggableManager

from tempo.users.models import User
from . import markdown


class Event(models.Model):
    code = models.CharField(max_length=200, db_index=True)
    slug = models.CharField(max_length=200, db_index=True, unique=True)
    verbose_name = models.CharField(max_length=200)
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        db_index=True,
        unique=True,
    )
    description = models.TextField(null=True, blank=True)
    creation_date = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(
        User,
        related_name='added_events',
        null=True,
        blank=True)

    users = models.ManyToManyField(
        User,
        related_name='events',
        through='EventConfig')

    class Meta:
        ordering = ('-creation_date', )

    def __str__(self):
        return self.verbose_name

    def save(self, **kwargs):
        if not self.slug:
            self.slug = self._get_slug()

        return super().save(**kwargs)

    def _get_slug(self):
        def unique_check(text, uids):
            if text in uids:
                return False
            return not Event.objects.filter(slug=text).exists()

        return slugify.UniqueSlugify(
            unique_check=unique_check,
            to_lower=True,
            max_length=190,
        )(self.verbose_name)


class EventConfig(models.Model):
    event = models.ForeignKey(
        Event,
        related_name='configs',
    )
    user = models.ForeignKey(
        User,
        related_name='event_configs',
    )
    creation_date = models.DateTimeField(default=timezone.now)
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return str(self.event)

    @property
    def title(self):
        return self.event.verbose_name


class EntryQuerySet(models.QuerySet):
    def with_score(self):
        score = models.F('importance') * models.F('like')
        return self.annotate(_score=score)

    def by_day(self, start, end, fill=False, serializer_class=None):
        if end <= start:
            raise ValueError('End must be greater than start')

        qs = self.prefetch_related('tags')
        qs = qs.order_by('-start')
        qs = qs.select_related('config__event').with_score()
        qs = qs.filter(
            start__date__gte=start,
            start__date__lte=end,
        )
        existing = collections.OrderedDict()
        # group existing values form database
        for k, g in itertools.groupby(qs, lambda e: e.start.date()):
            entries = list(g)
            final_entries = entries
            if serializer_class:
                final_entries = serializer_class(entries, many=True).data
            d = {
                'entries': final_entries,
                'date': k
            }
            d['score'] = sum([e.get_score() for e in entries])
            existing[k] = d

        final = []
        if fill:
            # fill missing dates
            dates = [start]
            while True:
                new_date = dates[-1] + datetime.timedelta(days=1)
                if new_date > end:
                    break
                dates.append(new_date)

            for date in sorted(dates, reverse=True):
                try:
                    final.append(existing[date])
                except KeyError:
                    final.append({
                        'date': date,
                        'score': 0,
                        'entries': []
                    })
        else:
            final = []
            for date, data in existing.items():
                final.append(data)
        return final

    def stats(self, period, start, end, fill=False, ordering='date'):
        periods = {
            'day': {
                'field': models.DateField(),
                'delta': {'days': 1},
                'type': 'date',
                'filter': lambda qs: qs.filter(
                    start__date__gte=start, start__date__lte=end)
            },
        }
        try:
            p = periods[period]
        except KeyError:
            raise ValueError('{} period not supported'.format(period))

        if start >= end:
            raise ValueError('end must be greater than start')

        qs = p['filter'](self)
        qs = qs.annotate(
            date=models.functions.Trunc(
                'start',
                kind=period,
                output_field=p['field']))
        qs = qs.order_by('date').values('date').annotate(
            score=models.Sum(models.F('importance') * models.F('like')),
            entries=models.Count('id'),
        )
        if not fill:
            return qs.order_by(ordering)

        if p['type'] == 'date':
            try:
                real_start = start.date()
            except AttributeError:
                real_start = start
            try:
                real_end = end.date()
            except AttributeError:
                real_end = end

        final = []
        delta = datetime.timedelta(**p['delta'])
        previous = real_start - delta
        qs = list(qs)
        i = 0
        while True:
            if previous >= real_end:
                break
            default = {
                'date': previous + delta,
                'score': 0,
                'entries': 0,
            }
            try:
                row = qs[i]
            except IndexError:
                # empty queryset, we just fill emptyy values
                final.append(default)
                previous = default['date']
                continue

            if default['date'] < row['date']:
                # we need to fill because next qs row is to far in the future
                final.append(default)
                previous = default['date']
                continue

            # otherwise, we're good to go, we increment the queryset row
            final.append(row)
            previous = row['date']
            i += 1

        if ordering.startswith('-'):
            final = reversed(final)
        return final


class Entry(models.Model):
    config = models.ForeignKey(
        EventConfig,
        related_name='entries',
    )
    is_public = models.BooleanField(default=False)

    LIKE_CHOICES = (
        (-4, _('awful')),
        (-2, _('bad')),
        (-1, _('negative')),
        (0, _('neutral')),
        (1, _('positive')),
        (2, _('good')),
        (4, _('great')),
    )
    like = models.IntegerField(default=0, choices=LIKE_CHOICES)
    IMPORTANCE_CHOICES = (
        (1, _('anectodic')),
        (2, _('small')),
        (4, _('high')),
        (8, _('very high')),
    )
    importance = models.IntegerField(default=1, choices=IMPORTANCE_CHOICES)
    start = models.DateTimeField(default=timezone.now, db_index=True)
    end = models.DateTimeField(null=True, blank=True, db_index=True)
    duration = models.DurationField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    detail_url = models.URLField(null=True, blank=True)
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        db_index=True,
        unique=True,
    )
    tags = TaggableManager()
    objects = EntryQuerySet.as_manager()

    class Meta:
        ordering = ('-start', )

    @property
    def hashtags(self):
        regex = re.compile(r"#(\w+)")
        return set(sorted(regex.findall(self.comment or '')))

    def get_score(self):
        try:
            return self._score
        except AttributeError:
            return self.like * self.importance

    @property
    def comment_rendered(self):
        return markdown.safe_markdown(self.comment or '')

    def save(self, **kwargs):
        self.clean()
        if self.end:
            self.duration = self.end - self.start
        return super().save(**kwargs)

    def set_tags(self):
        self.tags.add(*self.hashtags)

    def clean(self):
        if self.end and self.start > self.end:
            raise ValidationError('Start cannot be greater than end')
        super().clean()


@receiver(post_save, sender=Entry)
def set_tags(sender, instance, **kwargs):
    instance.set_tags()
