import factory

from tempo.users.tests.factories import UserFactory


class Event(factory.DjangoModelFactory):

    class Meta:
        model = 'events.Event'

    code = factory.Faker('word')
    verbose_name = factory.Faker('sentence')
    value_type = 'integer'
    description = factory.Faker('paragraph')
    default_value = 1


class Config(factory.DjangoModelFactory):

    class Meta:
        model = 'events.EventConfig'

    user = factory.SubFactory(UserFactory)
    event = factory.SubFactory(Event)


class Entry(factory.DjangoModelFactory):

    class Meta:
        model = 'events.Entry'

    config = factory.SubFactory(Config)
    value = factory.Faker('random_int')
