import json
import datetime
from django.core.serializers.json import DjangoJSONEncoder
from rest_framework.test import APITestCase
from test_plus.test import TestCase
from django.utils import timezone
from django.forms import ValidationError

from tempo.events import models
from . import factories
from .. import serializers


class TestEvent(APITestCase, TestCase):
    maxDiff = None

    def test_can_create_entry_from_api(self):
        user = self.make_user()
        config = factories.Config(user=user)
        payload = {
            'comment': 'hello',
            'detail_url': 'http://something.test',
            'config': config.pk,
            'start': timezone.now(),
            'tags': ['python', 'django'],
        }
        url = self.reverse('api:v1:events:entries-list')
        with self.login(user):
            response = self.client.post(
                url,
                data=payload,
                format='json',
            )
        entry = config.entries.latest('id')

        self.assertEqual(
            list(entry.tags.order_by('slug').values_list('slug', flat=True)),
            ['django', 'python'])
        self.assertEqual(entry.config, config)
        self.assertEqual(entry.comment, payload['comment'])
        self.assertEqual(entry.detail_url, payload['detail_url'])
        self.assertEqual(entry.start, payload['start'])

    def test_can_edit_entry_from_api(self):
        user = self.make_user()
        entry = factories.Entry(config__user=user)
        payload = {
            'comment': 'hello',
            'detail_url': 'http://something.test',
            'config': entry.config.pk,
            'start': timezone.now(),
            'tags': ['python', 'django'],
        }
        url = self.reverse(
            'api:v1:events:entries-detail', pk=entry.pk)
        with self.login(user):
            response = self.client.put(
                url,
                data=payload,
                format='json',
            )
        entry.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(entry.tags.order_by('slug').values_list('slug', flat=True)),
            ['django', 'python'])
        self.assertEqual(entry.comment, payload['comment'])
        self.assertEqual(entry.detail_url, payload['detail_url'])
        self.assertEqual(entry.start, payload['start'])

    def test_can_get_tags_from_api(self):
        user = self.make_user()
        entry = factories.Entry(config__user=user, tags=['python', 'django'])
        url = self.reverse(
            'api:v1:events:tags-list')
        with self.login(user):
            response = self.client.get(url)

        payload = json.loads(response.content.decode('utf-8'))

        expected = [
            {
                'name': 'python',
                'text': 'python',
                'value': 'python',
            },
            {
                'name': 'django',
                'text': 'django',
                'value': 'django',
            },
        ]
        self.assertEqual(len(payload), len(expected))
        for e in expected:
            self.assertIn(e, payload)

    def test_can_create_config_and_event_from_api(self):
        user = self.make_user()
        payload = {
            'verbose_name': 'hello',
        }
        url = self.reverse('api:v1:events:configs-list')
        with self.login(user):
            response = self.post(
                url,
                data=payload,
            )
        config = user.event_configs.latest('id')

        self.assertEqual(config.event.verbose_name, 'hello')
        self.assertEqual(config.user, user)

    def test_can_search_config(self):
        user = self.make_user()
        url = self.reverse('api:v1:search')
        config = factories.Config(
            event__verbose_name='hello', user=user)
        with self.login(user):
            response = self.client.get(
                url,
                {'q': 'hel', 'type': 'config'},
            )
        payload = json.loads(response.content.decode('utf-8'))
        expected = {
            'results': [
                {
                    'value': config.id,
                    'text': config.event.verbose_name,
                    'name': config.event.verbose_name,
                }
            ]
        }
        self.assertEqual(payload, expected)

    def test_can_group_by_day_from_api(self):
        now = timezone.now()
        yesterday = now - datetime.timedelta(days=1)
        two_days_ago = now - datetime.timedelta(days=2)
        config = factories.Config(
            event__verbose_name='hello')
        e1 = factories.Entry(
            start=now,
            config=config
        )
        e2 = factories.Entry(
            start=two_days_ago,
            config=config
        )
        qs = models.Entry.objects.by_day(
            start=two_days_ago.date(), end=now.date())

        url = self.reverse('api:v1:events:entries-byday')
        with self.login(config.user):
            response = self.client.get(
                url,
                {'start': two_days_ago.date(), 'end': now.date()}
            )

        expected = {
            'start': two_days_ago.date(),
            'end': now.date(),
            'days': [
                {
                    'date': now.date(),
                    'entries': serializers.EntryNestedSerializer([e1], many=True).data,
                    'score': 0,
                },
                {
                    'date': two_days_ago.date(),
                    'entries': serializers.EntryNestedSerializer([e2], many=True).data,
                    'score': 0,
                },
            ]
        }

        self.assertEqual(
            json.loads(response.content.decode('utf-8')),
            json.loads(DjangoJSONEncoder().encode(expected)),
        )

    def test_can_filter_group_by_day_by_tag(self):
        now = timezone.now()
        yesterday = now - datetime.timedelta(days=1)
        two_days_ago = now - datetime.timedelta(days=2)
        config = factories.Config(
            event__verbose_name='hello')
        e1 = factories.Entry(
            start=now,
            config=config,
            tags=['hello', 'is', 'it', 'me'],
        )
        e2 = factories.Entry(
            start=two_days_ago,
            config=config,
            tags=['hello', 'is'],
        )
        qs = models.Entry.objects.by_day(
            start=two_days_ago.date(), end=now.date())

        url = self.reverse('api:v1:events:entries-byday')
        with self.login(config.user):
            response = self.client.get(
                url,
                {
                    'start': two_days_ago.date(),
                    'end': now.date(),
                    'tags': 'hello,is,me',
                }
            )

        expected = {
            'start': two_days_ago.date(),
            'end': now.date(),
            'days': [
                {
                    'date': now.date(),
                    'entries': serializers.EntryNestedSerializer([e1], many=True).data,
                    'score': 0,
                },
            ]
        }
        self.assertEqual(
            json.loads(response.content.decode('utf-8')),
            json.loads(DjangoJSONEncoder().encode(expected)),
        )

    def test_can_filter_group_by_day_by_comment_content(self):
        now = timezone.now()
        yesterday = now - datetime.timedelta(days=1)
        two_days_ago = now - datetime.timedelta(days=2)
        config = factories.Config(
            event__verbose_name='test')
        e1 = factories.Entry(
            start=now,
            config=config,
            comment="hello"
        )
        e2 = factories.Entry(
            start=two_days_ago,
            config=config,
            comment="goodbye",
        )
        qs = models.Entry.objects.by_day(
            start=two_days_ago.date(), end=now.date())

        url = self.reverse('api:v1:events:entries-byday')
        with self.login(config.user):
            response = self.client.get(
                url,
                {
                    'start': two_days_ago.date(),
                    'end': now.date(),
                    'search': 'hel test',
                }
            )

        expected = {
            'start': two_days_ago.date(),
            'end': now.date(),
            'days': [
                {
                    'date': now.date(),
                    'entries': serializers.EntryNestedSerializer([e1], many=True).data,
                    'score': 0,
                },
            ]
        }
        self.assertEqual(
            json.loads(response.content.decode('utf-8')),
            json.loads(DjangoJSONEncoder().encode(expected)),
        )

    def test_can_filter_group_by_day_by_config(self):
        now = timezone.now()
        yesterday = now - datetime.timedelta(days=1)
        two_days_ago = now - datetime.timedelta(days=2)
        config1 = factories.Config(
            event__verbose_name='test1')
        config2 = factories.Config(
            event__verbose_name='test2',
            user=config1.user)
        e1 = factories.Entry(
            start=now,
            config=config1,
        )
        e2 = factories.Entry(
            start=two_days_ago,
            config=config2,
        )
        qs = models.Entry.objects.by_day(
            start=two_days_ago.date(), end=now.date())

        url = self.reverse('api:v1:events:entries-byday')
        with self.login(config1.user):
            response = self.client.get(
                url,
                {
                    'start': two_days_ago.date(),
                    'end': now.date(),
                    'config': config1.pk,
                }
            )

        expected = {
            'start': two_days_ago.date(),
            'end': now.date(),
            'days': [
                {
                    'date': now.date(),
                    'entries': serializers.EntryNestedSerializer([e1], many=True).data,
                    'score': 0,
                },
            ]
        }
        self.assertEqual(
            json.loads(response.content.decode('utf-8')),
            json.loads(DjangoJSONEncoder().encode(expected)),
        )

    def test_stats_entries(self):
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

        expected = {
            'start': str(two_days_ago.date()),
            'end': str(now.date()),
            'fill': True,
            'ordering': '-date',
            'results': [
                {
                    'date': str(now.date()),
                    'score': 3,
                    'entries': 2,
                },
                {
                    'date': str(yesterday.date()),
                    'score': 0,
                    'entries': 0,
                },
                {
                    'date': str(two_days_ago.date()),
                    'score': 12,
                    'entries': 2,
                },
            ]
        }

        url = self.reverse('api:v1:events:entries-stats')
        with self.login(config.user):
            response = self.client.get(
                url,
                {
                    'start': two_days_ago.date(),
                    'end': now.date(),
                    'fill': True,
                    'ordering': '-date',
                }
            )

        payload = json.loads(response.content.decode('utf-8'))

        self.assertEqual(payload, expected)

    # def test_user_timeline(self):
    #     e1 = factories.Entry()
    #     e2 = factories.Entry(
    #         config__user=e1.config.user,
    #     )
    #     e3 = factories.Entry(
    #         config__user=e1.config.user,
    #     )
    #
    #     url = self.reverse('events:timeline')
    #     with self.login(e1.config.user):
    #         response = self.get(
    #             url,)
    #
    #     expected = [e3, e2, e1]
    #     self.assertEqual(list(response.context['entries']), expected)
