from test_plus.test import TestCase
from django.utils import timezone
from django.forms import ValidationError

from tempo.events import models
from . import factories


class TestEvent(TestCase):
    def test_can_create_template(self):
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
        url = self.reverse('events:templates:create')
        with self.login(user):
            response = self.post(
                url,
                data=payload,
            )
        template = user.templates.latest('id')

        self.assertEqual(template.created_by, user)
        self.assertEqual(template.verbose_name, payload['verbose_name'])
        self.assertEqual(template.description, payload['description'])
        self.assertEqual(template.is_public, payload['is_public'])
        self.assertEqual(template.value_type, payload['value_type'])
        self.assertEqual(template.default_value, payload['default_value'])
        self.assertEqual(template.required_value, payload['required_value'])
        self.assertEqual(template.display_template, payload['display_template'])
