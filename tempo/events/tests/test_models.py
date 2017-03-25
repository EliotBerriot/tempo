import datetime
import html
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
            description='Use this event to record when you smoke',
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
            importance=2,
            like=-1,
        )
        entry.tags.add('health', 'bad')

        self.assertEqual(entry.get_score(), -2)
        self.assertEqual(entry.tags.count(), 2)

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

    def test_can_annotate_with_score(self):
        e1 = factories.Entry(
            importance=2,
            like=-1,
        )
        e2 = factories.Entry(
            importance=3,
            like=1,
        )
        e3 = factories.Entry(
            importance=4,
            like=-1,
        )
        expected = [-2, 3, -4]
        qs = models.Entry.objects.order_by('start').with_score()
        for i, e in enumerate(qs):
            self.assertEqual(e._score, expected[i])

    def test_hashtags_ar_registered_as_entry_tags(self):
        e = factories.Entry(
            comment='#yolo #coucou'
        )
        expected = {'coucou', 'yolo'}
        qs = e.tags.values_list('name', flat=True)
        self.assertEqual(e.hashtags, expected)
        self.assertEqual(set(qs), expected)

    def test_duration_is_populated_from_start_and_end(self):
        end = timezone.now()
        duration = datetime.timedelta(seconds=36588)
        start = end - duration
        e = factories.Entry(
            end=end,
            start=start
        )
        self.assertEqual(e.duration, duration)

    def test_end_must_be_greated_than_start(self):
        end = timezone.now()
        start = timezone.now() + datetime.timedelta(days=1)
        with self.assertRaises(ValidationError):
            e = factories.Entry(
                end=end,
                start=start
            )

    def test_can_render_comment_as_markdown(self):
        e = factories.Entry(
            comment="hello"
        )
        self.assertEqual(e.comment_rendered, '<p>hello</p>')

    def test_can_render_comment_as_markdown_skipping_html(self):
        e = factories.Entry(
            comment="<script>alert('hello');</script>"
        )
        expected = "<p>&lt;script&gt;alert('hello');&lt;/script&gt;</p>"

        self.assertEqual(e.comment_rendered, expected)

    def test_can_group_entries_by_day(self):
        now = timezone.now()
        yesterday = now - datetime.timedelta(days=1)
        two_days_ago = now - datetime.timedelta(days=2)
        e1 = factories.Entry(
            start=now
        )
        e2 = factories.Entry(
            start=two_days_ago
        )
        qs = models.Entry.objects.by_day(
            start=two_days_ago.date(), end=now.date(), fill=True)
        expected = [
            {
                'date': now.date(),
                'entries': [e1],
                'score': 0,
            },
            {
                'date': yesterday.date(),
                'entries': [],
                'score': 0,
            },
            {
                'date': two_days_ago.date(),
                'entries': [e2],
                'score': 0,
            },
        ]

        for i, row in enumerate(qs):
            self.assertEqual(row['date'], expected[i]['date'])
            self.assertEqual(list(row['entries']), expected[i]['entries'])

    def test_score_by_day(self):
        now = timezone.now()
        yesterday = now - datetime.timedelta(days=1)
        two_days_ago = now - datetime.timedelta(days=2)

        # day 1
        e1 = factories.Entry(
            start=now,
            like=1,
            importance=2,  # score 2
        )
        config = e1.config
        e2 = factories.Entry(
            start=now,
            like=1,
            importance=1,  # score 1
            config=config
        )

        # two days ago
        e3 = factories.Entry(
            start=two_days_ago,
            like=-2,
            config=config,
            importance=2,  # score -4
        )
        e4 = factories.Entry(
            start=two_days_ago,
            like=4,
            importance=4,  # score 16
            config=config
        )
        qs = list(models.Entry.objects.all().stats(
                'day', start=two_days_ago, end=now
            ).order_by('-date'))
        expected = [
            {
                'date': now.date(),
                'score': 3,
                'entries': 2,
            },
            {
                'date': two_days_ago.date(),
                'score': 12,
                'entries': 2,
            },
        ]

        for i, row in enumerate(expected):
            self.assertEqual(qs[i]['score'], row['score'])
            self.assertEqual(qs[i]['entries'], row['entries'])
            self.assertEqual(qs[i]['date'], row['date'])

        qs = list(models.Entry.objects.all().stats(
                'day', start=two_days_ago, end=now, ordering='-date', fill=True
            ))
        expected = [
            {
                'date': now.date(),
                'score': 3,
                'entries': 2,
            },
            {
                'date': yesterday.date(),
                'score': 0,
                'entries': 0,
            },
            {
                'date': two_days_ago.date(),
                'score': 12,
                'entries': 2,
            },
        ]

        for i, row in enumerate(expected):
            self.assertEqual(qs[i]['score'], row['score'])
            self.assertEqual(qs[i]['entries'], row['entries'])
            self.assertEqual(qs[i]['date'], row['date'])
