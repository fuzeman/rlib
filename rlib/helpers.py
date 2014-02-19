import HTMLParser
import re

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
    if not s:
        return s

    return h.unescape(s)


def re_compile(pattern, flags):
    if type(pattern) is not list:
        pattern = [pattern]

    return [re.compile(x, flags) for x in pattern]


def re_match(regex, value, single=True):
    if type(regex) is not list:
        regex = [regex]

    matches = []

    for r in regex:
        match = r.match(value)

        if match:
            matches.append(match)

            if single:
                break

    if single:
        return matches[0] if matches else None

    return matches
