from rest_framework import serializers
from taggit.models import Tag

from . import models


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Event
        fields = (
            'uuid',
            'verbose_name',
        )


class TagSerializer(serializers.ModelSerializer):
    value = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    text = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = (
            'name',
            'value',
            'text',
        )

    def get_value(self, obj):
        return obj.slug

    def get_text(self, obj):
        return obj.slug

    def get_name(self, obj):
        return obj.slug


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


class StringListField(serializers.ListField):
    child = serializers.CharField()

    def to_representation(self, data):
        return ','.join(data.values_list('name', flat=True))


class EntrySerializer(serializers.ModelSerializer):
    tags = StringListField()
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
            'tags',
        )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        instance = super().create(validated_data)
        instance.tags.set(*tags, clear=True)
        return instance

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        instance = super().update(instance, validated_data)
        instance.tags.set(*tags, clear=True)
        return instance
