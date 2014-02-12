from rlib import html_unescape, validate_object
from datetime import datetime
import urlparse


class Thing(object):
    def __init__(self, json):
        data = json['data']

        self.id = data.get('id')

        self.name = data.get('name')
        self.full_name = data.get('name')

        self.kind = json.get('kind')

    @staticmethod
    def parse(reddit, json):
        kind = json.get('kind')

        if kind == 't1':
            return Comment(reddit, json)
        elif kind == 't2':
            return Account(reddit, json)
        elif kind == 't3':
            return Link(reddit, json)
        elif kind == 't5':
            return Subreddit(reddit, json)
        else:
            raise NotImplementedError()


class Content(Thing):
    def __init__(self, json):
        super(Content, self).__init__(json)

        data = json['data']

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


class Comment(Content):
    prefix = 't1'

    URL_COMMENT_PERMALINK = "/r/%s/comments/%s/_/%s"

    def __init__(self, reddit, json):
        super(Comment, self).__init__(json)

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
                if comment.get('kind') != 't1':
                    continue

                self.replies.append(Comment(reddit, comment))

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
            Comment.URL_COMMENT_PERMALINK % (
                comment.subreddit, link_id, comment.id
            )
        )


class Account(Thing):
    prefix = 't2'

    URL_OVERVIEW = "/user/%s.json"
    URL_COMMENTS = "/user/%s/comments.json"
    URL_LINKS = "/user/%s/submitted.json"
    URL_SUBSCRIBED_SUBREDDITS = "/subreddits/mine.json"

    def __init__(self, reddit, json):
        super(Account, self).__init__(json)

        self._reddit = reddit
        data = json['data']

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
        return Listing(self._reddit, Account.URL_COMMENTS % self.name)

    def get_posts(self):
        pass

    def get_subscribed_subreddits(self):
        pass


class Link(Content):
    prefix = 't3'

    def __init__(self, reddit, json):
        super(Link, self).__init__(json)

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


class Subreddit(Thing):
    prefix = 't5'

    def __init__(self, reddit, json):
        super(Subreddit, self).__init__(json)

        data = json['data']

        self.title = data.get('title')
        self.display_name = data.get('display_name')

        self.url = data.get('url')

        self.created = datetime.fromtimestamp(data.get('created'))
        self.created_utc = datetime.utcfromtimestamp(data.get('created_utc'))

        self.subscribers = data.get('subscribers')
        self.accounts_active = data.get('accounts_active')

        self.header_img = data.get('header_img')
        self.header_size = data.get('header_size')
        self.header_title = data.get('header_title')

        self.submit_text = data.get('submit_text')
        self.submit_text_html = html_unescape(data.get('submit_text_html'))
        self.submit_text_label = data.get('submit_text_label')
        self.submit_link_label = data.get('submit_link_label')

        self.description = data.get('description')
        self.description_html = html_unescape(data.get('description_html'))
        self.public_description = data.get('public_description')

        self.user_is_banned = data.get('user_is_banned')
        self.user_is_moderator = data.get('user_is_moderator')
        self.user_is_subscriber = data.get('user_is_subscriber')
        self.user_is_contributor = data.get('user_is_contributor')

        self.over18 = data.get('over18')
        self.public_traffic = data.get('public_traffic')
        self.subreddit_type = data.get('subreddit_type')
        self.submission_type = data.get('submission_type')
        self.comment_score_hide_mins = data.get('comment_score_hide_mins')

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

        json = self._reddit.request(url)

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
