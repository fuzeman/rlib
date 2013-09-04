from rlib import Reddit

__author__ = 'Dean Gardiner'

if __name__ == '__main__':
    reddit = Reddit()

    user = reddit.get_user('<username>')

    for comment in user.get_comments():
        full_comment = reddit.get_comment(comment.subreddit, comment.link_id, comment.id)
        if full_comment:
            if len(full_comment.replies) > 0:
                link_id = comment.link_id
                if link_id.startswith("t3_"):
                    link_id = link_id[3:]
                print "http://reddit.com/r/%s/comments/%s/foo/%s" % (comment.subreddit, link_id, comment.id)
