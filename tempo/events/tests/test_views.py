import json

from test_plus.test import TestCase
from django.utils import timezone
from django.forms import ValidationError

from tempo.events import models
from . import factories


class TestEvent(TestCase):
    def test_can_create_entry_from_api(self):
        user = self.make_user()
        config = factories.Config(user=user)
        payload = {
            'comment': 'hello',
            'detail_url': 'http://something.test',
            'config': config.pk,
            'start': timezone.now(),
        }
        url = self.reverse('api:v1:events:entries-list')
        with self.login(user):
            response = self.post(
                url,
                data=payload,
            )
        entries = config.entries.latest('id')

        self.assertEqual(entries.config, config)
        self.assertEqual(entries.comment, payload['comment'])
        self.assertEqual(entries.detail_url, payload['detail_url'])
        self.assertEqual(entries.start, payload['start'])

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
