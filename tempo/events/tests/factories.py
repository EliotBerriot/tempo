import factory
from django.utils import timezone

from tempo.users.tests.factories import UserFactory


class Event(factory.DjangoModelFactory):

    class Meta:
        model = 'events.Event'

    code = factory.Faker('word')
    verbose_name = factory.Faker('sentence')
    description = factory.Faker('paragraph')


class Config(factory.DjangoModelFactory):

    class Meta:
        model = 'events.EventConfig'

    user = factory.SubFactory(UserFactory)
    event = factory.SubFactory(Event)


class Entry(factory.DjangoModelFactory):

    class Meta:
        model = 'events.Entry'

    config = factory.SubFactory(Config)
    start = factory.LazyAttribute(lambda o: timezone.now())
    detail_url = factory.Faker('url')
    comment = factory.Faker('paragraph')

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        self.tags.add(*extracted)
