from rest_framework import serializers

from . import models


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Event
        fields = (
            'uuid',
            'verbose_name',
        )


class ConfigSerializer(serializers.ModelSerializer):
    event = EventSerializer()

    class Meta:
        model = models.EventConfig
        fields = (
            'id',
            'event',
            'event',
            'is_public',
        )


class EntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Entry
        fields = (
            'uuid',
            'start',
            'end',
            'comment',
            'detail_url',
            'like',
            'importance',
            'is_public',
            'config',
        )
