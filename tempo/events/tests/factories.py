import factory

from tempo.users.tests.factories import UserFactory


class Template(factory.DjangoModelFactory):

    class Meta:
        model = 'events.Template'

    code = factory.Faker('word')
    verbose_name = factory.Faker('sentence')
    value_type = 'integer'
    description = factory.Faker('paragraph')
    default_value = 1


class Event(factory.DjangoModelFactory):

    class Meta:
        model = 'events.Event'

    user = factory.SubFactory(UserFactory)
    template = factory.SubFactory(Template)
    value = factory.Faker('random_int')
