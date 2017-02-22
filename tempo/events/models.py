import uuid
import slugify

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

from tempo.users.models import User


class Template(models.Model):
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
        related_name='added_templates',
        null=True,
        blank=True)

    users = models.ManyToManyField(User, related_name='templates')

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
            return not Template.objects.filter(slug=text).exists()

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
            '{user} added event "{name}" with value {value}'
        )
        return template.format(
            user=user_string,
            name=self.verbose_name,
            value=value)

    def format_value(self, value):
        if self.value_type == 'integer':
            return int(value)
        return value


class Event(models.Model):
    template = models.ForeignKey(Template, related_name='events')
    user = models.ForeignKey(User, related_name='events')
    is_public = models.BooleanField(default=False)
    value = models.DecimalField(
        max_digits=20,
        decimal_places=10,
        null=True,
        blank=True)
    time = models.DateTimeField(default=timezone.now, db_index=True)
    comment = models.TextField(null=True, blank=True)
    detail_url = models.URLField(null=True, blank=True)
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        db_index=True,
        unique=True,
    )

    class Meta:
        ordering = ('-time', )

    def save(self, **kwargs):
        if not self.pk and self.value is None:
            self.value = self.template.get_default_value()

        self.clean()
        return super().save(**kwargs)

    def clean(self):
        super().clean()
        if self.template.required_value and self.value is None:
            raise ValidationError('Value is required')

    @property
    def formatted_value(self):
        if self.value:
            return self.template.format_value(self.value)
        return

    def display_text(self, owner=True):
        if owner:
            user = 'you'
        else:
            user = self.user.username

        return self.template.get_display_text(
            user_string=user, value=self.formatted_value)
