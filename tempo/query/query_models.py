import persisting_theory

from tempo.events import models


class ModelRegistry(persisting_theory.Registry):
    def prepare_name(self, data, name=None):
        return data.code

    def prepare_data(self, data):
        return data()

    def get_by_source(self, source):
        return [v for v in self.values() if v.source == source][0]
query_models = ModelRegistry()


class QueryModel(object):
    pass


@query_models.register
class Entry(QueryModel):
    code = 'entry'
    source = 'entries'
    model = models.Entry
