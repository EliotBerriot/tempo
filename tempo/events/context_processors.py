from django.conf import settings
from . import models as m


def models(request):
    return {
        'Entry': m.Entry
    }


def timezone(request):
    return {
        'default_timezone': settings.TIME_ZONE
    }


def raven(request):
    return {
        'js_dsn': settings.RAVEN_JS_DSN
    }
