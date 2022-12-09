#!/usr/bin/env python
# file: ytfd.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2019 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2019-07-28T13:42:58+0200
# Last modified: 2022-12-09T09:36:48+0100
"""View or download the latest video's from your favorite youtube channels."""

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
#     "count": 3,
#     "viewer": "mpv",
#     "viewer-args": "",
#     "downloader": "yt-dlp",
#     "downloader-args": "-S res:720 --",
#     "channels": {
#         "first channel name": "UC7QoixBiFO2zstyEXkbVpVg",
#         "second channel name": "UCvY8pgX_3ksKvZBNFHVoUAQ",
#         "third channel name": "UCk3wqxZummX-HTzYGjHDBpw"
#     }
# }
# The “limit” is optional. If not present, it will be set to 7 days.
# Also optional is “count”. If not present, it will be set to 3 videos
# "viewer", “viewer-args”, “downloader” and “downloader-args” are also optional.
# If not present, it will be set with the default values.
# Note that the channelId's above are not real, they're randomly generated!
# You can find the “channelId” in the source of the channel's homepage.
rcpath = os.environ["HOME"] + os.sep + ".ytfdrc"


def _check(settings, key, tp, default):
    """
    Verify that a setting exists and is the right type and return it.
    If not, return the default value.
    """
    if key not in settings:
        return default
    if not isinstance(settings[key], tp):
        return default
    return settings[key]


with open(rcpath) as rc:
    settings = json.load(rc)
    # Unpack data for use. Other keys are ignored.
    channels = settings["channels"]
    limit = _check(settings, "limit", int, 7)
    count = _check(settings, "count", int, 3)
    viewer = _check(settings, "viewer", str, "mpv")
    viewer_args = _check(settings, "viewer-args", str, "")
    if viewer_args:
        viewer = " ".join([viewer, viewer_args])
    downloader = _check(settings, "downloader", str, "yt-dlp")
    downloader_args = _check(settings, "downloader-args", str, "-S res:720 --")
    if downloader_args:
        downloader = " ".join([downloader, downloader_args])


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
        (html.unescape(title), link.rsplit("=")[1], date)
        for title, link, date in zip(titles, links, published)
        if "watch" in link and (now - date).days < limit
    )
    if not items:
        # print(f"No video's less than {limit} days old found for “{channel_title}”.\n")
        continue
    if len(items) > count:
        items = items[:count-1]
    print(f"Channel “{channel_title}”")
    for title, link, date in items:
        print(f"∙ title: “{title}”")
        print(f"   date: {date}")
        print(f"   view: {viewer} 'https://www.youtube.com/watch?v={link}' &")
        print(f"   download: {downloader} {link}")
    print()
