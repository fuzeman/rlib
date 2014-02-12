from rlib.helpers import validate_object, html_unescape, re_compile, re_match
from rlib.interfaces import SubredditInterface, AccountInterface
from rlib.things import Thing, Account
import urllib2
import json
import re

__author__ = 'Dean Gardiner'
__version__ = "0.2.2"


class Reddit(object):
    ACCOUNT_PATTERNS = [
        r"^(?P<domain>(\w+\.)?\w+\.\w+)?\/(user|u)\/(?P<username>\w+)$",
        r"^(?P<username>\w+)$"
    ]

    SUBREDDIT_PATTERNS = [
        r"^(?P<domain>(\w+\.)?\w+\.\w+)?\/r\/(?P<subreddit>\w+)$",
        r"^(?P<subreddit>\w+)\.(?P<domain>\w+\.\w+)$",
        r"^(?P<subreddit>\w+)$"
    ]

    def __init__(self, use_https=True, domain="reddit.com", user_agent=None):
        self.use_https = use_https
        self.domain = domain

        self.user_agent = user_agent + ' ' if user_agent else ''
        self.user_agent += "rlib/" + __version__

        self._account_regex = re_compile(self.ACCOUNT_PATTERNS, re.IGNORECASE)
        self._subreddit_regex = re_compile(self.SUBREDDIT_PATTERNS, re.IGNORECASE)

    def account(self, identifier, domain=None):
        return self._get_interface(AccountInterface, self._account_regex, identifier, domain)

    def subreddit(self, identifier, domain=None):
        return self._get_interface(SubredditInterface, self._subreddit_regex, identifier, domain)

    def request(self, url):
        print 'Requesting "%s"' % url

        request = urllib2.Request(url)
        request.add_header('User-Agent', self.user_agent)

        response = urllib2.urlopen(request)
        return json.loads(response.read())

    def _get_interface(self, interface, regex, identifier, domain=None):
        match = re_match(regex, identifier)
        if not match:
            raise ValueError('Unable to match subreddit identifier')

        match = match.groupdict()

        # Add default domain if one is specified
        if not match.get('domain'):
            match['domain'] = domain or self.domain

        return interface(self, **match)
