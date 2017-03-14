import uuid
import slugify
import re

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver

from taggit.managers import TaggableManager

from tempo.users.models import User


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

    def save(self, **kwargs):
        self.clean()
        return super().save(**kwargs)

    def set_tags(self):
        self.tags.add(*self.hashtags)

    def clean(self):
        super().clean()


@receiver(post_save, sender=Entry, dispatch_uid="set_tags")
def set_tags(sender, instance, **kwargs):
    instance.set_tags()
