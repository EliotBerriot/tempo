from test_plus.test import TestCase

from django.db.models import F
from taggit.models import Tag
from tempo.query import language, runner
from tempo.events import models


class TestRunner(TestCase):

    def test_can_run_simple_query_against_query(self):
        q = 'SELECT uuid as u, start AS s FROM entries'
        result = runner.execute(q)
        expected = models.Entry.objects.annotate(
            u=F('uuid'), s=F('start')).values('u', 's')

        self.assertEqual(str(expected.query), str(result.query))
    # 
    # def test_can_run_simple_query_against_events(self):
    #     q = 'SELECT verbose_name FROM events'
    #     result = runner.execute(q)
    #     expected = models.Event.objects.annotate(
    #         s=F('verbose_name')).values('s')
    #
    #     self.assertEqual(str(expected.query), str(result.query))
