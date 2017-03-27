import datetime


def rank_by_closest(iterable, attribute, dt):
    results = []
    today = datetime.datetime.today()
    ref = datetime.datetime.combine(today, dt.time())
    for e in iterable:
        a = datetime.datetime.combine(today, getattr(e, attribute).time())
        delta = abs((ref - a).total_seconds()) or 1
        results.append((1 / delta, e))

    return sorted(results, key=lambda v: v[0], reverse=True)
