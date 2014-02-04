from datetime import datetime
import json
import urllib2
import urlparse
from rlib.helpers import validate_object, html_unescape

__author__ = 'Dean Gardiner'


class Reddit(object):
    __version__ = "0.12"

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

    DOMAIN = "www.reddit.com"

    def __init__(self, user_agent=None):
        self.domain = Reddit.DOMAIN

        self.user_agent = user_agent + ' ' if user_agent else ''
        self.user_agent += "rlib/" + self.__version__

    def get_user(self, name):
        json = self._request(Reddit.URL_USER_INFO % name)
        return RedditUser(self, json)

    def get_comment(self, subreddit=None, link_id=None, comment_id=None, url=None, include_link=False):
        if not url:
            if not subreddit or not link_id or not comment_id:
                raise ValueError('Either the "subreddit", "link_id" and "comment_id" or "url" parameters are required')

            if link_id.startswith("t3_"):
                link_id = link_id[3:]

            if comment_id.startswith("t1_"):
                comment_id = comment_id[3:]

            url = self._prepend_domain(Reddit.URL_GET_COMMENT % (subreddit, link_id, comment_id))

        response = self._request(url, prepend_domain=False)
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

        response = self._request(url, prepend_domain=False)
        if len(response) < 1:
            return None

        return Thing.parse(self, response[0]["data"]["children"][0])

    def _prepend_domain(self, path):
        return "http://%s%s" % (self.domain, path)

    def _request(self, url, prepend_domain=True):
        url = self._prepend_domain(url) if prepend_domain else url

        request = urllib2.Request(url)
        request.add_header('User-Agent', self.user_agent)

        response = urllib2.urlopen(request)
        return json.loads(response.read())


class Thing(object):
    def __init__(self, json):
        data = json['data']

        self.full_name = data.get('name')
        self.id = data.get('id')
        self.kind = json.get('kind')

    @staticmethod
    def parse(reddit, json):
        kind = json.get('kind')

        if kind == 't1':
            return RedditComment(reddit, json)
        elif kind == 't2':
            return RedditUser(reddit, json)
        elif kind == 't3':
            return RedditLink(reddit, json)
        else:
            raise NotImplementedError()


class RedditUser(Thing):
    URL_OVERVIEW = "/user/%s.json"
    URL_COMMENTS = "/user/%s/comments.json"
    URL_LINKS = "/user/%s/submitted.json"
    URL_SUBSCRIBED_SUBREDDITS = "/subreddits/mine.json"

    def __init__(self, reddit, json):
        super(RedditUser, self).__init__(json)

        self._reddit = reddit
        data = json['data']

        self.name = data.get('name')

        self.link_karma = data.get('link_karma')
        self.comment_karma = data.get('comment_karma')

        self.created = datetime.fromtimestamp(data.get('created'))
        self.created_utc = datetime.utcfromtimestamp(data.get('created_utc'))

        self.has_mail = data.get('has_mail')
        self.has_mod_mail = data.get('has_mod_mail')
        self.has_verified_email = data.get('has_verified_email')

        self.is_friend = data.get('is_friend')
        self.is_gold = data.get('is_gold')
        self.is_mod = data.get('is_mod')

        self.over_18 = data.get('over_18')

        validate_object(self, data)

    def get_overview(self):
        pass

    def get_comments(self):
        return Listing(self._reddit, RedditUser.URL_COMMENTS % self.name)

    def get_posts(self):
        pass

    def get_subscribed_subreddits(self):
        pass


class RedditContent(Thing):
    def __init__(self, json):
        super(RedditContent, self).__init__(json)

        data = json['data']

        self.name = data.get('name')

        self.author = data.get('author')
        self.author_flair_css_class = data.get('author_flair_css_class')
        self.author_flair_text = data.get('author_flair_text')

        self.banned_by = data.get('banned_by')
        self.approved_by = data.get('approved_by')

        self.saved = data.get('saved')

        self.created = datetime.fromtimestamp(data.get('created'))
        self.created_utc = datetime.utcfromtimestamp(data.get('created_utc'))

        self.edited = data.get('edited')
        self.distinguished = data.get('distinguished')

        self.ups = data.get('ups')
        self.downs = data.get('downs')
        self.likes = data.get('likes')
        self.score_hidden = data.get('score_hidden')

        self.num_reports = data.get('num_reports')

        self.subreddit = data.get('subreddit')
        self.subreddit_id = data.get('subreddit_id')



class RedditComment(RedditContent):
    URL_COMMENT_PERMALINK = "/r/%s/comments/%s/_/%s"

    def __init__(self, reddit, json):
        super(RedditComment, self).__init__(json)

        self._reddit = reddit
        data = json['data']

        self.body = data.get('body')
        self.body_html = html_unescape(data.get('body_html'))

        self.gilded = data.get('gilded')

        self.parent_id = data.get('parent_id')

        self.link_id = data.get('link_id')
        self.link_title = data.get('link_title')

        # Parse replies
        self.replies = []
        if data["replies"] and len(data["replies"]) > 0:
            for comment in data["replies"]["data"]["children"]:
                self.replies.append(RedditComment(reddit, comment))

        validate_object(self, data, ['replies'])

        # Create permalink
        self.permalink = self.create_permalink("http://%s" % self._reddit.domain, self)

    @staticmethod
    def create_permalink(base, comment):
        link_id = comment.link_id
        if link_id.startswith("t3_"):
            link_id = link_id[3:]

        return urlparse.urljoin(
            base,
            RedditComment.URL_COMMENT_PERMALINK % (
                comment.subreddit, link_id, comment.id
            )
        )


class RedditLink(RedditContent):
    def __init__(self, reddit, json):
        super(RedditLink, self).__init__(json)

        self._reddit = reddit
        data = json['data']

        self.title = data.get('title')
        self.url = data.get('url')
        self.domain = data.get('domain')
        self.thumbnail = data.get('thumbnail')

        self.link_flair_css_class = data.get('link_flair_css_class')
        self.link_flair_text = data.get('link_flair_text')

        self.stickied = data.get('stickied')
        self.clicked = data.get('clicked')
        self.visited = data.get('visited')
        self.is_self = data.get('is_self')
        self.over_18 = data.get('over_18')
        self.hidden = data.get('hidden')

        self.selftext = data.get('selftext')
        self.selftext_html = html_unescape(data['selftext_html']) if data.get('selftext_html') else None

        self.score = data.get('score')

        self.num_comments = data.get('num_comments')

        self.media = data.get('media')
        self.media_embed = data.get('media_embed')

        self.secure_media = data.get('secure_media')
        self.secure_media_embed = data.get('secure_media_embed')

        self.permalink = 'http://%s%s' % (self._reddit.domain, data.get('permalink'))

        validate_object(self, data)


class Listing(object):
    def __init__(self, reddit, url):
        self._reddit = reddit
        self._url = url

        self._before = None
        self._after = None
        self._cur_page_index = None
        self._cur_page = None

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def _fetch_next_page(self):
        url = self._url
        if self._after:
            if '?' in url:
                url += '&after=' + self._after
            else:
                url += '?after=' + self._after

        json = self._reddit._request(url)

        if json.get('kind') != 'Listing':
            raise Exception()

        self._parse_page(json)

    def _parse_page(self, json):
        data = json['data']
        children = data['children']

        self._cur_page = []
        for child in children:
            self._cur_page.append(Thing.parse(self._reddit, child))

        self._after = data.get('after')
        self._before = data.get('before')

        self._cur_page_index = 0

    def next(self):
        if not self._cur_page:
            self._fetch_next_page()

        self._cur_page_index += 1

        if self._cur_page_index >= len(self._cur_page):
            if not self._after:
                raise StopIteration()

            self._fetch_next_page()

        return self._cur_page[self._cur_page_index]
