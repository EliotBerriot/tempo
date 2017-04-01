from django.db.models import F
from taggit.models import Tag

from tempo.events import models

from . import language
from . import query_models



def execute(q):
    parsed_query = language.query.parseString(q)
    return STATEMENT_MAPPING[parsed_query['statement']](parsed_query)


def run_select(parsed_query):
    query_model = query_models.query_models.get_by_source(parsed_query['source'])

    aliases = {}
    values = []
    for full_expr in parsed_query['exprs']:
        if full_expr.get('alias'):
            a = full_expr['alias']
            n = full_expr['expr']['column']
            aliases[a] = F(n)
            values.append(a)
        else:
            values.append(full_expr['expr']['column'])

    qs = query_model.model.objects.all()

    if aliases:
        qs = qs.annotate(**aliases)
    qs = qs.values(*values)
    return qs


STATEMENT_MAPPING = {
    'SELECT': run_select,
}
