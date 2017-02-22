from test_plus.test import TestCase
from django.utils import timezone
from django.forms import ValidationError

from tempo.events import models
from . import factories


class TestEvent(TestCase):
    def test_can_create_event_type(self):

        t = models.Template.objects.create(
            slug='smoked',
            verbose_name='Smoked a cigarette',
            value_type='integer',
            description='Use this event to record when you smoke',
            default_value=1,
            display_template='{user} smoked {value} cigarette(s)',
        )
        u = self.make_user()
        u.templates.add(t)

        e = models.Event.objects.create(
            template=t,
            user=u,
            time=timezone.now(),
            comment='Just smoked one, bad idea...',
            detail_url=None,
        )

        self.assertEqual(e.value, 1)
        self.assertEqual(
            e.display_text(),
            'you smoked 1 cigarette(s)')

    def test_can_autopopulate_slug_from_verbose_name(self):
        t = factories.Template(
            verbose_name='Hello world',
        )
        self.assertEqual(t.slug, 'hello-world')

    def test_can_deduplicate_slug(self):
        t1 = factories.Template(
            verbose_name='Hello world',
        )
        self.assertEqual(t1.slug, 'hello-world')

        t2 = factories.Template(
            verbose_name='Hello world',
        )
        self.assertEqual(t2.slug, 'hello-world-1')

    def test_can_require_value(self):

        allow_empty = factories.Event(
            template__required_value=False,
            template__default_value=None,
            value=None
        )
        with self.assertRaises(ValidationError):
            factories.Event(
                template__required_value=True,
                template__default_value=None,
                value=None
            )
