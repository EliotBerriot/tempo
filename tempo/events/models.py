import uuid
import slugify

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

from tempo.users.models import User


class Event(models.Model):
    code = models.CharField(max_length=200, db_index=True)
    slug = models.CharField(max_length=200, db_index=True, unique=True)
    verbose_name = models.CharField(max_length=200)
    is_public = models.BooleanField(default=False)
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        db_index=True,
        unique=True,
    )
    VALUE_TYPE_CHOICES = [
        ('integer', 'integer'),
    ]
    default_value = models.DecimalField(
        max_digits=20,
        decimal_places=10,
        null=True,
        blank=True)
    required_value = models.BooleanField(default=True)
    value_type = models.CharField(
        max_length=50, choices=VALUE_TYPE_CHOICES, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    creation_date = models.DateTimeField(default=timezone.now)
    display_template = models.TextField(
        null=True,
        blank=True,
    )
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

    def get_default_value(self):
        return self.default_value

    def get_display_text(self, user_string, value):
        template = (
            self.display_template or
            '{user} added entry "{name}" with value {value}'
        )
        return template.format(
            user=user_string,
            name=self.verbose_name,
            value=value)

    def format_value(self, value):
        if self.value_type == 'integer':
            return int(value)
        return value


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


class Entry(models.Model):
    config = models.ForeignKey(
        EventConfig,
        related_name='entries',
    )
    is_public = models.BooleanField(default=False)
    value = models.DecimalField(
        max_digits=20,
        decimal_places=10,
        null=True,
        blank=True)
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

    class Meta:
        ordering = ('-start', )

    def save(self, **kwargs):
        if not self.pk and self.value is None:
            self.value = self.config.event.get_default_value()

        self.clean()
        return super().save(**kwargs)

    def clean(self):
        super().clean()
        if self.config.event.required_value and self.value is None:
            raise ValidationError('Value is required')

    @property
    def formatted_value(self):
        if self.value:
            return self.config.event.format_value(self.value)
        return

    def display_text(self, owner=True):
        if owner:
            user = 'you'
        else:
            user = self.user.username

        return self.config.event.get_display_text(
            user_string=user, value=self.formatted_value)
