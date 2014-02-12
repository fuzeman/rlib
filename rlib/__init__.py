from rlib.helpers import validate_object, html_unescape, re_compile, re_match
from rlib.interfaces import SubredditInterface
from rlib.things import Thing, Account
import urllib2
import json
import re

__author__ = 'Dean Gardiner'
__version__ = "0.12"


class Reddit(object):
    SUBREDDIT_PATTERNS = [
        r"^(?P<domain>(\w+\.)?\w+\.\w+)?\/r\/(?P<subreddit>\w+)$",
        r"^(?P<subreddit>\w+)\.(?P<domain>\w+\.\w+)$"
    ]

    URL_SSL_LOGIN = "https://ssl.reddit.com/api/login"
    URL_LOGIN = "/api/login/username"

    URL_USER_INFO = "/user/%s/about.json"
    URL_ME = "/api/me.json"
    URL_SUBREDDIT_ABOUT = "/r/%s/about.json"
    URL_COMPOSE_MESSAGE = "/api/compose"
    URL_REGISTER_ACCOUNT = "/api/register"
    URL_GET_THING = "/by_id/%s.json"
    URL_GET_COMMENT = "/r/%s/comments/%s/_/%s.json"
    URL_GET_LINK = "/r/%s/comments/%s.json"

    DOMAIN = "reddit.com"

    def __init__(self, user_agent=None):
        self.domain = Reddit.DOMAIN

        self.use_https = True

        self.user_agent = user_agent + ' ' if user_agent else ''
        self.user_agent += "rlib/" + __version__

        self._subreddit_regex = re_compile(self.SUBREDDIT_PATTERNS, re.IGNORECASE)

    def __getitem__(self, value):
        match = re_match(self._subreddit_regex, value)
        if not match:
            raise ValueError('Unable to match subreddit identifier')

        match = match.groupdict()

        # Add default domain if one is specified
        if not match['domain']:
            match['domain'] = self.DOMAIN

        return SubredditInterface(self, match.get('domain'), match.get('subreddit'))

    def get_user(self, name):
        json = self.request(Reddit.URL_USER_INFO % name)
        return Account(self, json)

    def get_comment(self, subreddit=None, link_id=None, comment_id=None, url=None, include_link=False):
        if not url:
            if not subreddit or not link_id or not comment_id:
                raise ValueError('Either the "subreddit", "link_id" and "comment_id" or "url" parameters are required')

            if link_id.startswith("t3_"):
                link_id = link_id[3:]

            if comment_id.startswith("t1_"):
                comment_id = comment_id[3:]

            url = self._prepend_domain(Reddit.URL_GET_COMMENT % (subreddit, link_id, comment_id))

        response = self.request(url, prepend_domain=False)
        if len(response) < 2:
            return None

        if len(response[1]["data"]["children"]) < 1:
            return None

        comment = Thing.parse(self, response[1]["data"]["children"][0])

        if include_link:
            link = Thing.parse(self, response[0]["data"]["children"][0])
            return link, comment

        return comment

    def get_link(self, subreddit=None, link_id=None, url=None):
        if not url:
            if not subreddit or not link_id:
                raise ValueError('Either the "subreddit" and "link_id"" or "url" parameters are required')

            if link_id.startswith("t3_"):
                link_id = link_id[3:]

            url = self._prepend_domain(Reddit.URL_GET_LINK % (subreddit, link_id))

        response = self.request(url, prepend_domain=False)
        if len(response) < 1:
            return None

        return Thing.parse(self, response[0]["data"]["children"][0])

    def _prepend_domain(self, path):
        return "http://%s%s" % (self.domain, path)

    def request(self, url, prepend_domain=True):
        url = self._prepend_domain(url) if prepend_domain else url

        request = urllib2.Request(url)
        request.add_header('User-Agent', self.user_agent)

        response = urllib2.urlopen(request)
        return json.loads(response.read())
