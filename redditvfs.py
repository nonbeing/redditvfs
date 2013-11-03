#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
This is a demo/proof of concept for the reddit virtual filesystem
quick-and-dirty
"""
import errno
import fuse
import stat
import time
import praw
import getpass
import ConfigParser
import sys

fuse.fuse_python_api = (0, 2)


def sanitize_filepath(path):
    """
    Converts provided path to legal UNIX filepaths.
    """
    # '/' is illegal
    path = path.replace('/', '_')
    # Direntry() doesn't seem to like non-ascii
    path = path.encode('ascii', 'ignore')
    return path


class redditvfs(fuse.Fuse):
    def __init__(self, reddit=None, *args, **kw):
        fuse.Fuse.__init__(self, *args, **kw)

        if reddit is None:
            raise Exception('reddit must be set')

    def getattr(self, path):
        """
        returns stat info for file, such as permissions and access times.
        """
        # default nlink and time info
        st = fuse.Stat()
        st.st_nlink = 2
        st.st_atime = int(time.time())
        st.st_mtime = st.st_atime
        st.st_ctime = st.st_atime
        # set if filetype and permissions
        if path.split('/')[-1] == '.' or path.split('/')[-1] == '..':
            # . and ..
            st.st_mode = stat.S_IFDIR | 0444
        elif path in ['/', '/u', '/r']:
            # top-level directories
            st.st_mode = stat.S_IFDIR | 0444
        elif len(path.split('/')) == 3 and path.split('/')[1] == 'r':
            # r/*/ - subreddits
            st.st_mode = stat.S_IFDIR | 0444
        elif len(path.split('/')) == 4 and path.split('/')[1] == 'r':
            # r/*/* - posts
            st.st_mode = stat.S_IFDIR | 0444
        else:
            st.st_mode = stat.S_IFREG | 0444
        return st

    def readdir(self, path, offset):
        """
        returns a list of directories in requested path
        """

        # Every directory has '.' and '..'
        yield fuse.Direntry('.')
        yield fuse.Direntry('..')
        r = praw.Reddit(user_agent='redditvfs')

        if path == '/':
            # top-level directory
            yield fuse.Direntry('u')
            yield fuse.Direntry('r')
        elif path == '/r':
            # if user is logged in, populate with get_my_subreddits
            # otherwise, default to frontpage
            # TODO: check if logged in
            # TODO: figure out how to get non-logged-in default subreddits,
            # falling back to get_popular_subreddits
            for subreddit in reddit.get_popular_subreddits():
                dirname = sanitize_filepath(subreddit.url.split('/')[2])
                yield fuse.Direntry(dirname)
        elif len(path.split('/')) == 3 and path.split('/')[1] == 'r':
            # posts in subreddits
            subreddit = path.split('/')[2]
            # TODO: maybe not hardcode limit?
            for post in r.get_subreddit(subreddit).get_hot(limit=10):
                filename = sanitize_filepath(sanitize_filepath(post.title)
                        + ' ' + post.id)
                yield fuse.Direntry(filename)
        elif len(path.split('/')) == 4 and path.split('/')[1] == 'r':
            # a post in a subreddit

            # get post id.  To make this user-friend it will be appended to
            # human-readable filenames, but this should work if it is the only
            # part of the filename as well.  The human-readable part is
            # dropped.
            if path.rfind(' ') > path.rfind('/'):
                post_id = path.split(' ')[-1]
            else:
                post_id = path.split('/')[-1]
            post = r.get_submission(submission_id = post_id)
            if post.thumbnail != "":
                # there is a thumbnail
                yield fuse.Direntry('thumbnail')


def login_get_username(config):
    """
    returns the username of the user to login
    """
    try:
        username = config.get('login', 'username')
    except Exception, e:
        # Prompt for username
        username = raw_input("Username: ")
        pass
    return username


def login_get_password(config):
    """
    returns the password of the user to login
    """
    try:
        password = config.get('login', 'password')
    except Exception, e:
        # Prompt for password
        password = getpass.getpass()
        pass
    return password


if __name__ == '__main__':
    # Create a reddit object from praw
    reddit = praw.Reddit(user_agent='redditvfs')

    # Login only if a configuration file is present
    if '-c' in sys.argv:
        # Remove '-c' from sys.argv
        sys.argv.remove('-c')

        # User wants to use the config file, create the parser
        config = ConfigParser.RawConfigParser(allow_no_value=True)

        # Check for default login
        try:
            config.read('~/.redditvfs.conf')
        except Exception, e:
            pass
        finally:
            username = login_get_username(config=config)
            password = login_get_password(config=config)
            try:
                reddit.login(username=username, password=password)
                print 'Logged in as: ' + username
            except Exception, e:
                print e
                print 'Failed to login'

    fs = redditvfs(reddit=reddit)
    fs.parse(errex=1)
    fs.main()
