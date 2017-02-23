from test_plus.test import TestCase
from django.utils import timezone
from django.forms import ValidationError

from tempo.events import models
from . import factories


class TestEvent(TestCase):
    def test_can_create_event(self):
        user = self.make_user()
        payload = {
            'verbose_name': 'My Template',
            'required_value': False,
            'default_value': 42,
            'value_type': 'integer',
            'is_public': True,
            'description': 'This is my first template',
            'display_template': 'Nope',
        }
        url = self.reverse('events:events:create')
        with self.login(user):
            response = self.post(
                url,
                data=payload,
            )
        events = user.events.latest('id')

        self.assertEqual(events.created_by, user)
        self.assertEqual(events.verbose_name, payload['verbose_name'])
        self.assertEqual(events.description, payload['description'])
        self.assertEqual(events.is_public, payload['is_public'])
        self.assertEqual(events.value_type, payload['value_type'])
        self.assertEqual(events.default_value, payload['default_value'])
        self.assertEqual(events.required_value, payload['required_value'])
        self.assertEqual(events.display_template, payload['display_template'])

    def test_user_timeline(self):
        e1 = factories.Entry()
        e2 = factories.Entry(
            config__user=e1.config.user,
        )
        e3 = factories.Entry(
            config__user=e1.config.user,
        )

        url = self.reverse('events:log')
        with self.login(e1.config.user):
            response = self.get(
                url,)

        expected = [e3, e2, e1]
        self.assertEqual(list(response.context['entries']), expected)
