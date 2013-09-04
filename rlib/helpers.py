__author__ = 'Dean Gardiner'


def validate_object(obj, data, ignore=None):
    if not ignore:
        ignore = []

    missing = {}

    for key, value in data.items():
        if not hasattr(obj, key) or getattr(obj, key) != value:
            if key not in ignore:
                missing[key] = value

    if len(missing) > 0:
        print "Object missing some keys:", missing