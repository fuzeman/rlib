from rlib.things import Thing


class RedditBase(object):
    def __init__(self, reddit, domain):
        self._reddit = reddit

        self.domain = domain

    def _build_url(self, path):
        return 'http%s://%s/%s.json' % (
            's' if self._reddit.use_https else '',
            self.domain,
            path
        )

    def request(self, path):
        url = self._build_url(path)

        print 'Requesting "%s"' % url
        return self._reddit.request(url, prepend_domain=False)

    def get(self, path):
        return Thing.parse(self._reddit, self.request(path))
