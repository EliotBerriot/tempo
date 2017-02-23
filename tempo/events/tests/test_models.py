from test_plus.test import TestCase
from django.utils import timezone
from django.forms import ValidationError

from tempo.events import models
from . import factories


class TestEvent(TestCase):
    def test_can_create_event(self):

        event = models.Event.objects.create(
            slug='smoked',
            verbose_name='Smoked a cigarette',
            value_type='integer',
            description='Use this event to record when you smoke',
            default_value=1,
            display_template='{user} smoked {value} cigarette(s)',
        )
        u = self.make_user()
        config = event.configs.create(
            user=u,
        )

        entry = models.Entry.objects.create(
            config=config,
            start=timezone.now(),
            comment='Just smoked one, bad idea...',
            detail_url=None,
        )

        self.assertEqual(entry.value, 1)
        self.assertEqual(
            entry.display_text(),
            'you smoked 1 cigarette(s)')

    def test_can_autopopulate_slug_from_verbose_name(self):
        event = factories.Event(
            verbose_name='Hello world',
        )
        self.assertEqual(event.slug, 'hello-world')

    def test_can_deduplicate_slug(self):
        event1 = factories.Event(
            verbose_name='Hello world',
        )
        self.assertEqual(event1.slug, 'hello-world')

        event2 = factories.Event(
            verbose_name='Hello world',
        )
        self.assertEqual(event2.slug, 'hello-world-1')

    def test_can_require_value(self):

        allow_empty = factories.Entry(
            config__event__required_value=False,
            config__event__default_value=None,
            value=None
        )
        with self.assertRaises(ValidationError):
            factories.Entry(
                config__event__required_value=True,
                config__event__default_value=None,
                value=None
            )
