import json
from rest_framework.test import APITestCase
from test_plus.test import TestCase
from django.utils import timezone
from django.forms import ValidationError

from tempo.events import models
from . import factories


class TestEvent(APITestCase, TestCase):
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
    # def test_user_timeline(self):
    #     e1 = factories.Entry()
    #     e2 = factories.Entry(
    #         config__user=e1.config.user,
    #     )
    #     e3 = factories.Entry(
    #         config__user=e1.config.user,
    #     )
    #
    #     url = self.reverse('events:log')
    #     with self.login(e1.config.user):
    #         response = self.get(
    #             url,)
    #
    #     expected = [e3, e2, e1]
    #     self.assertEqual(list(response.context['entries']), expected)
