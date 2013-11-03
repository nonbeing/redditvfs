redditVFS
========


Description
-----------
**reddivfs** is a FUSE-based filesystem that allows the user to read, post, and explore the content aggregation site reddit by maniplulating files and directories. The goal is to provide feature-complete access to the website via your file browser of choice.

Setup
-----
redditvfs runs off Python 2.3+. Once Python 2.3+ has been installed and all paths are set, redditvfs can then be run without any setup. However, if the user wishes to log in, a config file must be set up.

If a config file is used, but is empty or noncomplete, then redditvfs will prompt the user to input any missing information from the config.

Usage
-----
Default usage is
`./redditvfs.py [options] <mount-point>`

Once redditvfs is running, one can navigate from the mount point like a regular file system.

File System
-----------

The top-level mountpoint holds several directories and any config files in the following configuration.

        user1.conf
        r/
        u/
        m/

`r/` holds different subreddits. Subreddits can be subscribed or unsubscribed by `rmdir <subreddit>` the subreddit directory to unsubscribe, and `mkdir <subreddit name>` to subscribe.

Inside each subreddit directory, each post is another directory which contains a file with the post contents and all comments.

`u/` holds user information. `ls <username>` returns the files

        overview/
        comments/
        submitted/
        gilded/

Each directory holds the relevant comments or submissions as a symlink to the relevant post or comment in r/

`m/` holds the messages of the user in two directories, should one be logged in. One directory, `sent/` holds all sent messages from the user. The other, `inbox/` holds all messages received. To compose a message, a new text file is created in the directory `m/`, with the username of the recipient as the name of the file, and the contents of the file being the contents of the message.

The `r/` Directory
------------------
The first level of the `r/` directory holds all subreddits currently subscribed to. To subscribe to a subreddit, you `mkdir <subreddit-name>`. To unsubscribe, you `rmdir <subreddit-name>`

Each directory is named after the subreddit it contains.

Each subreddit directory contains multiple 'post directories.' Each post directory is named from the post it represents and a unique ID. Inside the directory there is

        content         -holds the contents of the post, be it a self-post or a link. 
        raw_content     -holds the raw contents of the post or comment
        link_content    -appears when a url is provided to reddit. Typically this can be used to view files.
        reply           -a special file that when written to will reply to the current parent.
        thumbnail       -a special file that appears when a thumbnail is generated by reddit.
        votes           -when read gives the number of upvotes and downvotes the post has. 
                         You can write a 1 (upvote), 0 (no vote) or -1 (downvote) to the file to vote. 
        flat            -Holds the contents of the post and all children comments. 
        <username>      -symlink to the user profile of the user who made the post.

The directory also contains several 'comment directories.'

Each comment directory corrosponds to the child comments. A comment directory has the same layout as a post directory, and can also contain comment directories of its own. The file `contents` instead contains the comment.

To make a post, you can write to the file `post` in the subreddit directory, with the first line being the title and the rest of the file being the contents.

To post a comment, inside any comment directory (or a post directory to make a top-elevel comment) you can write to `reply`. The contents are the comment itself.

To delete your post or comment, delete the `raw_content` file in the directory of the post or comment. If you have the correct permissions, the post or comment will be deleted.

To edit a post or comment, edit the `raw_content` file.



Options
-------
`-c -config [optional-config-file]` Designates a config files that may be empty, noncomplete, or filled out. If no config file is given, `.redditvfs.conf` is used.
`-f -foreground` Forces redditvfs to run in the foreground instead of in daemon mode. Useful for debugging.
