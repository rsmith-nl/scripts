#!/usr/bin/env python3
# file: blocklists.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2020 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2020-08-15T20:24:57+0200
# Last modified: 2020-08-15T22:46:46+0200
"""Generate blocklistst for dnsmasq and unbound"""

# Data
facebook = [
    "cdninstagram.com", "edgekey.net", "edgesuite.net", "facebook.com", "facebook.net",
    "fb.com", "fb.me", "fbcdn.com", "fbcdn.net", "fbsbx.com", "instagram.com",
    "tfbnw.net", "whatsapp.com"
]

# Data based on the 80-domain list from:
# https://www.reddit.com/r/privacy/comments/3tz3ph/blocking_most_advertising_servers_via_factory/
ads = [
    "207.net", "247realmedia.com", "2o7.net", "2mdn.net", "33across.com", "abmr.net",
    "acoda.net", "adblade.com", "adbrite.com", "adbureau.net", "adchemy.com",
    "addthis.com", "addthisedge.com", "admeld.com", "admob.com", "adsense.com",
    "adsonar.com", "advertising.com", "afy11.net", "aquantive.com", "atdmt.com",
    "atwola.com", "channelintelligence.com", "cmcore.com", "coremetrics.com",
    "crowdscience.com", "decdna.net", "decideinteractive.com", "doubleclick.com",
    "doubleclick.net", "esomniture.com", "fimserve.com", "flingwebads.com",
    "foxnetworks.com", "google-analytics.com", "googleadservices.com",
    "googlesyndication.com", "gravity.com", "hitbox.com", "imiclk.com",
    "imrworldwide.com", "insightexpress.com", "insightexpressai.com", "intellitxt.com",
    "invitemedia.com", "leadback.com", "lindwd.net", "mookie1.com", "myads.com",
    "netconversions.com", "nexac.com", "nextaction.net", "nielsen-online.com",
    "offermatica.com", "omniture.com", "omtrdc.net", "pm14.com", "quantcast.com",
    "quantserve.com", "realmedia.com", "revsci.net", "rightmedia.com", "rmxads.com",
    "ru4.com", "rubiconproject.com", "samsungadhub.com", "scorecardresearch.com",
    "sharethis.com", "shopthetv.com", "targetingmarketplace.com", "themig.com",
    "trendnetcloud.com", "yieldmanager.com", "yieldmanager.net", "yldmgrimg.net",
    "youknowbest.com", "yumenetworks.com"
]

# Some additions from myself.  These are based on ads that I've seen myself
# and domains that often occur in the someonewhocares blocklist.
ads += [
    "runative-syndicate.com", "cnzz.com", "fastclick.net", "p2l.info", "oewabox.at",
    "am15.net", "checkm8.com", "adtech.de", "adtech.fr", "adtech.us", "sitemeter.com",
    "petrovka.info", "admob.com", "adscience.nl", "adengage.com"
]

# Remove doubles, sort the list.
ads = sorted(set(ads))

# IP address to redirect to for Unbound.  Typically, you would set your firewall to deny
# access to this particular IP address.
ip = "127.0.0.2"

print("#### DNSMASQ ####")
for kind, name in ((facebook, "facebook"), (ads, 'ads')):
    print(f'# Block {name}')
    for domain in kind:
        print(f"address=/{domain}/")
    print()

print("#### UNBOUND ####")
print("server:")
for kind, name in ((facebook, "facebook"), (ads, 'ads')):
    print(f'    # Block {name}')
    for domain in kind:
        print(f'    local-zone: "{domain}" redirect')
        print(f'    local-data: "{domain}" A {ip}')
    print()
