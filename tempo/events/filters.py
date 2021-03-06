import re
import django_filters
from . import models


import re

from django.db.models import Q


def normalize_query(query_string,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    """ Splits the query string in invidual keywords, getting rid of unecessary spaces
        and grouping quoted words together.
        Example:

        >>> normalize_query('  some random  words "with   quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']

    """
    return [
        normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)]


def get_query(query_string, search_fields):
    """ Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.

    """
    query = None  # Query to search for every search term
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None  # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query


class TagsFilter(django_filters.CharFilter):

    def filter(self, qs, value):
        if not value:
            return qs

        tags = value.split(',')
        for tag in tags:
            q = Q(tags__slug__iexact=tag) | Q(tags__name__iexact=tag)
            qs = qs.filter(q)

        return qs.distinct()


class SearchFilter(django_filters.CharFilter):
    def __init__(self, *args, **kwargs):
        self.search_fields = kwargs.pop('search_fields')
        super().__init__(*args, **kwargs)

    def filter(self, qs, value):
        if not value:
            return qs

        query = get_query(value, self.search_fields)

        return qs.filter(query).distinct()


class EntryFilter(django_filters.FilterSet):
    tags = TagsFilter()
    search = SearchFilter(
        search_fields=[
            'comment', 'config__event__verbose_name', 'detail_url'])

    class Meta:
        model = models.Entry
        fields = ['tags', 'search', 'config']
