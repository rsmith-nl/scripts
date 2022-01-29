#!/usr/bin/env python
# file: ytfd.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2019 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2019-07-28T13:42:58+0200
# Last modified: 2021-08-11T00:07:03+0200
"""Get the latest video's from your favorite youtube channels.

    This script now generates commands for the mpv viewer that force it
    to use youtube-dl.  This was done so I could limit the quality of the
    downloaded clips to my screen resolution.
"""

import datetime
import html
import json
import os
import re
import urllib.request
import sys

base = "https://www.youtube.com/feeds/videos.xml?channel_id="
now = datetime.datetime.now(tz=datetime.timezone.utc)

# Read limit and channels from the configuration file.
# The file format is JSON, as shown below:
# {
#     "limit": 7,
#     "viewer": "mpv",
#     "channels": {
#         "first channel name": "UC7QoixBiFO2zstyEXkbVpVg",
#         "second channel name": "UCvY8pgX_3ksKvZBNFHVoUAQ",
#         "third channel name": "UCk3wqxZummX-HTzYGjHDBpw"
#     }
# }
# The “limit” is optional. If not present, it will be set to 7 days.
# The "viewer" is also optional. If not present, it will be set to 'mpv'.
# Note that the channelId's above are not real, they're randomly generated!
# You can find the “channelId” in the source of the channel's homepage.
rcpath = os.environ["HOME"] + os.sep + ".ytfdrc"
with open(rcpath) as rc:
    settings = json.load(rc)
    channels = settings["channels"]
    if "limit" in settings:
        limit = settings["limit"]
    else:
        limit = 7
    if "viewer" in settings:
        viewer = settings["viewer"]
    else:
        viewer = "mpv"


# Flush after every line.
sys.stdout.reconfigure(line_buffering=True)
# Retrieve and print video information
for channel_title, channel_id in channels.items():
    try:
        with urllib.request.urlopen(base + channel_id) as con:
            text = con.read().decode("utf-8")
            rv = con.code
    except urllib.error.HTTPError:
        rv = -1
    if rv != 200:
        print(
            f"Could not retrieve data for “{channel_title}” (code: {rv}), skipping it.\n"
        )
        continue
    titles = re.findall("<title>(.*)</title>", text, re.IGNORECASE)
    links = re.findall('<link rel="alternate" href="(.*)"/>', text, re.IGNORECASE)
    published = [
        datetime.datetime.fromisoformat(pt)
        for pt in re.findall("<published>(.*)</published>", text, re.IGNORECASE)
    ]
    items = tuple(
        (html.unescape(title), link, date)
        for title, link, date in zip(titles, links, published)
        if "watch" in link and (now - date).days < limit
    )
    if not items:
        # print(f"No video's less than {limit} days old found for “{channel_title}”.\n")
        continue
    print(f"Channel “{channel_title}”")
    for title, link, date in items:
        print(f"∙ title: “{title}”")
        print(f"   date: {date}")
        print(f"   view: {viewer} '{link}' &")
    print()
