from . import models as m


def models(request):
    return {
        'Entry': m.Entry
    }
