import HTMLParser

__author__ = 'Dean Gardiner'


h = HTMLParser.HTMLParser()


def validate_object(obj, data, ignore=None):
    if not ignore:
        ignore = []

    missing = {}

    for key, value in data.items():
        if not hasattr(obj, key):
            if key not in ignore:
                missing[key] = value

    if len(missing) > 0:
        print "Object missing some keys:", missing


def html_unescape(s):
    return h.unescape(s)
