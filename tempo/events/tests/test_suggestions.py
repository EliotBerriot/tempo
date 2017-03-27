import datetime
import html
from test_plus.test import TestCase
from django.utils import timezone

from tempo.events import models
from tempo.events import suggestions

from . import factories


class TestSuggestions(TestCase):

    def test_can_rank_events_by_time(self):
        now = timezone.now()
        thirty_minutes_ago = now - datetime.timedelta(minutes=30)
        two_hours_ago = now - datetime.timedelta(hours=2)

        e1 = factories.Entry(
            start=now,
        )
        e2 = factories.Entry(
            start=thirty_minutes_ago,
        )
        e3 = factories.Entry(
            start=two_hours_ago,
        )

        qs = models.Entry.objects.all()
        s = suggestions.rank_by_closest(qs, 'start', now)
        self.assertEqual(
            [e for score, e in s],
            [e1, e2, e3]
        )

        s = suggestions.rank_by_closest(qs, 'start', thirty_minutes_ago)

        self.assertEqual(
            [e for score, e in s],
            [e2, e1, e3]
        )

        s = suggestions.rank_by_closest(qs, 'start', two_hours_ago)
        self.assertEqual(
            [e for score, e in s],
            [e3, e2, e1]
        )
