from rlib.core import RedditBase
from rlib.things import Thing
import urllib


class Interface(RedditBase):
    pass


class AccountInterface(Interface):
    def __init__(self, reddit, domain, username):
        super(AccountInterface, self).__init__(reddit, domain)

        self.name = username

    def about(self):
        return self.get('about')

    def _build_url(self, path):
        return super(AccountInterface, self)._build_url('user/%s/%s' % (self.name, path))

    def __str__(self):
        return '<rlib.SubReddit %s>' % ', '.join([
            ('%s: %s' % (x, repr(getattr(self, x))))
            for x in ['domain', 'name']
        ])

    def __repr__(self):
        return str(self)


class SubredditInterface(Interface):
    def __init__(self, reddit, domain, subreddit):
        super(SubredditInterface, self).__init__(reddit, domain)

        self.name = subreddit

    def about(self):
        return self.get('about')

    def comments(self, article, comment=None, include_comments=True, include_link=False, limit=None, context=None):
        if not include_comments:
            limit = 1

        parameters = dict([(k, v) for (k, v) in [
            ('limit', limit),
            ('context', context)
        ] if v])

        # TODO clean request url generation up
        response = self.request('comments/%s/_%s.json%s' % (
            article,
            ('/' + comment) if comment else '',
            ('?%s' % urllib.urlencode(parameters)) if parameters else ''
        ))

        if len(response) < 2:
            return None

        if len(response[1]["data"]["children"]) < 1:
            return None

        result = []

        if include_comments:
            result.append(Thing.parse(self, response[1]["data"]["children"][0]))

        if include_link:
            result.append(Thing.parse(self, response[0]["data"]["children"][0]))

        if len(result) == 1:
            return result[0]

        return tuple(result)

    # TODO don't request comments
    def link(self, article):
        return self.comments(article, include_comments=False, include_link=True)

    def _build_url(self, path):
        return super(SubredditInterface, self)._build_url('r/%s/%s' % (self.name, path))

    def __str__(self):
        return '<rlib.SubReddit %s>' % ', '.join([
            ('%s: %s' % (x, repr(getattr(self, x))))
            for x in ['domain', 'name']
        ])

    def __repr__(self):
        return str(self)
