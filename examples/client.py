import pprint
import sys
from rlib import Reddit

__author__ = 'Dean Gardiner'

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Missing username parameter"
        exit()

    reddit = Reddit()

    user = reddit.get_user(sys.argv[1])

    for comment in user.get_comments():
        full_comment = reddit.get_comment(comment.subreddit, comment.link_id, comment.id)
        if full_comment:
            if len(full_comment.replies) > 0:
                print full_comment.permalink
