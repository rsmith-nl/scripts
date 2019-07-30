#!/usr/bin/env python3
# file: youtube-feed.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2019 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2019-07-28T13:42:58+0200
# Last modified: 2019-07-30T23:56:08+0200
"""Get the latest video's from your favorite youtube channels."""

import datetime
import html
import json
import os
import re
import requests
import sys

base = 'https://www.youtube.com/feeds/videos.xml?channel_id='
now = datetime.datetime.now(tz=datetime.timezone.utc)

# Read limit and channels from the configuration file.
# The file format is JSON, as shown below:
# {
#     "limit": 7,
#     "channels": {
#         "first channel name": "UC7QoixBiFO2zstyEXkbVpVg",
#         "second channel name": "UCvY8pgX_3ksKvZBNFHVoUAQ",
#         "third channel name": "UCk3wqxZummX-HTzYGjHDBpw"
#     }
# }
# The “limit” is optional. If not present, it will be set to 7 days.
# Note that the channelId's above are not real, they're randomly generated!
# You can find the “channelId” in the source of the channel's homepage.
rcpath = os.environ['HOME'] + os.sep + '.youtube-feedrc'
with open(rcpath) as rc:
    settings = json.load(rc)
    channels = settings['channels']
    if 'limit' in settings:
        limit = settings['limit']
    else:
        limit = 7

# Flush after every line.
sys.stdout.reconfigure(line_buffering=True)
# Retrieve and print video information
for channel_title, channel_id in channels.items():
    res = requests.get(base + channel_id)
    if not res.ok:
        print(f'Could not retrieve data for “{channel_title}”, skipping it.\n')
        continue
    titles = re.findall('<title>(.*)</title>', res.text, re.IGNORECASE)
    links = re.findall('<link rel="alternate" href="(.*)"/>', res.text, re.IGNORECASE)
    published = [
        datetime.datetime.fromisoformat(pt) for pt in
        re.findall('<published>(.*)</published>', res.text, re.IGNORECASE)
    ]
    items = tuple(
        (html.unescape(title), link, date)
        for title, link, date in zip(titles, links, published)
        if 'watch' in link and (now-date).days < limit
    )
    if not items:
        print(f"No video's less than {limit} days old found for “{channel_title}”.\n")
        continue
    print(f"Channel “{channel_title}”")
    for title, link, date in items:
        print(f"∙ title: “{title}”")
        print(f"   date: {date}")
        print(f"   link: “{link}”")
    print()
