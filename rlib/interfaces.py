from rlib.core import RedditBase
from rlib.things import Thing


class SubredditInterface(RedditBase):
    def __init__(self, reddit, domain, name):
        super(SubredditInterface, self).__init__(reddit, domain)

        self.name = name

    def about(self):
        return self.get('about')

    def comments(self, article, comment=None, include_link=False):
        response = self.request('comments/%s/_%s' % (
            article,
            ('/' + comment) if comment else ''
        ))
        if len(response) < 2:
            return None

        if len(response[1]["data"]["children"]) < 1:
            return None

        comment = Thing.parse(self, response[1]["data"]["children"][0])

        if include_link:
            link = Thing.parse(self, response[0]["data"]["children"][0])
            return link, comment

        return comment

    def _build_url(self, path):
        return super(SubredditInterface, self)._build_url('/r/%s/%s' % (self.name, path))

    def __str__(self):
        return '<rlib.SubReddit %s>' % ', '.join([
            ('%s: %s' % (x, repr(getattr(self, x))))
            for x in ['domain', 'name']
        ])

    def __repr__(self):
        return str(self)
