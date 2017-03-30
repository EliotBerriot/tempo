from django.utils import timezone
from django.core.urlresolvers import reverse
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
        return [
            data.name for data in data.all()
        ]


class EntrySerializer(serializers.ModelSerializer):
    tags = StringListField(required=False)
    score = serializers.SerializerMethodField()
    update_url = serializers.SerializerMethodField()
    comment_rendered = serializers.SerializerMethodField()
    comment_rendered = serializers.SerializerMethodField()

    class Meta:
        model = models.Entry
        fields = (
            'uuid',
            'start',
            'end',
            'comment',
            'comment_rendered',
            'detail_url',
            'update_url',
            'like',
            'importance',
            'is_public',
            'config',
            'tags',
            'score',
        )

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        instance = super().create(validated_data)
        instance.tags.set(*tags, clear=True)
        instance.set_tags()
        return instance

    def get_score(self, obj):
        return obj.get_score()

    def get_update_url(self, obj):
        return reverse('api:v1:events:entries-detail',
                       kwargs={'uuid': str(obj.uuid)})

    def get_comment_rendered(self, obj):
        return obj.comment_rendered

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', [])
        instance = super().update(instance, validated_data)
        instance.tags.set(*tags, clear=True)
        instance.set_tags()
        return instance


class EntryNestedSerializer(EntrySerializer):
    config = ConfigSerializer()
