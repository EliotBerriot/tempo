from test_plus.test import TestCase

from django.db.models import F
from tempo.query import language, runner
from tempo.events import models


class TestQueryLanguage(TestCase):

    def test_column(self):
        q = 'test'

        result = language.column.parseString(q)

        self.assertEqual(result['column'], 'test')

    def test_function(self):
        q = 'COUNT'

        result = language.function.parseString(q)

        self.assertEqual(result['function'], 'COUNT')

    def test_function_call(self):
        q = 'COUNT(score)'

        result = language.function_call.parseString(q)

        self.assertEqual(result['function'], 'COUNT')
        self.assertEqual(result['arguments'][0], 'score')

    def test_function_call_with_multiple_arguments(self):
        q = 'COUNT(score, test)'

        result = language.function_call.parseString(q)

        self.assertEqual(result['function'], 'COUNT')
        self.assertEqual(result['arguments'][0], 'score')
        self.assertEqual(result['arguments'][1], 'test')

    def test_alias_expr(self):
        q = 'AS t'

        result = language.alias_expr.parseString(q)

        self.assertEqual(result['alias'], 't')

    def test_expr(self):
        q = 'COUNT(score)'

        result = language.expr.parseString(q)

        self.assertEqual(result['function'], 'COUNT')
        self.assertEqual(result['arguments'][0], 'score')

        q = 'score'

        result = language.expr.parseString(q)

        self.assertEqual(result['column'], 'score')

    def test_full_expr(self):
        q = 'COUNT(score) as t'

        result = language.full_expr.parseString(q)

        self.assertEqual(result['expr']['function'], 'COUNT')
        self.assertEqual(result['expr']['arguments'][0], 'score')
        self.assertEqual(result['alias'], 't')

    def test_exprs(self):
        q = 'COUNT(score) as t, hello'

        result = language.exprs.parseString(q)

        self.assertEqual(result[0]['full_expr']['expr']['function'], 'COUNT')
        self.assertEqual(result[0]['full_expr']['expr']['arguments'][0], 'score')
        self.assertEqual(result[0]['full_expr']['alias'], 't')
        self.assertEqual(result[1]['full_expr']['expr']['column'], 'hello')

    def test_source(self):
        q = 'FROM entries'

        result = language.source.parseString(q)

        self.assertEqual(result['source'], 'entries')

    def test_select(self):
        q = 'SELECT COUNT(score) as t, hello FROM entries'

        result = language.query.parseString(q)

        self.assertEqual(result['statement'], 'SELECT')
        self.assertEqual(result['source'], 'entries')
        self.assertEqual(result['exprs'][0]['full_expr']['expr']['function'], 'COUNT')
        self.assertEqual(result['exprs'][0]['full_expr']['expr']['arguments'][0], 'score')
        self.assertEqual(result['exprs'][0]['full_expr']['alias'], 't')
        self.assertEqual(result['exprs'][1]['full_expr']['expr']['column'], 'hello')
