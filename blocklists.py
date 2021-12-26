#!/usr/bin/env python
# file: blocklists.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2020 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2020-08-15T20:24:57+0200
# Last modified: 2021-12-19T23:07:24+0100
"""Generate blocklistst for dnsmasq and unbound"""

# Data
facebook = [
    "cdninstagram.com",
    "edgesuite.net",
    "facebook.com",
    "facebook.de",
    "facebook.fr",
    "facebook.net",
    "fb.com",
    "fbcdn.com",
    "fbcdn.net",
    "fbsbx.com",
    "freebasics.com",
    "instagram.com",
    "internet.org",
    "online-metrix.net",
    "tfbnw.net",
    "thefacebook.com",
    "whatsapp.com",
    "whatsapp.net",
]

# Data based on the 80-domain list from:
# https://www.reddit.com/r/privacy/comments/3tz3ph/blocking_most_advertising_servers_via_factory/
ads = [
    "207.net",
    "247realmedia.com",
    "2o7.net",
    "2mdn.net",
    "33across.com",
    "abmr.net",
    "acoda.net",
    "adblade.com",
    "adbrite.com",
    "adbureau.net",
    "adchemy.com",
    "addthis.com",
    "addthisedge.com",
    "admeld.com",
    "admob.com",
    "adsense.com",
    "adsonar.com",
    "advertising.com",
    "afy11.net",
    "aquantive.com",
    "atdmt.com",
    "atwola.com",
    "channelintelligence.com",
    "cmcore.com",
    "coremetrics.com",
    "crowdscience.com",
    "decdna.net",
    "decideinteractive.com",
    "doubleclick.com",
    "doubleclick.net",
    "esomniture.com",
    "fimserve.com",
    "flingwebads.com",
    "foxnetworks.com",
    "google-analytics.com",
    "googleadservices.com",
    "googlesyndication.com",
    "gravity.com",
    "hitbox.com",
    "imiclk.com",
    "imrworldwide.com",
    "insightexpress.com",
    "insightexpressai.com",
    "intellitxt.com",
    "invitemedia.com",
    "leadback.com",
    "lindwd.net",
    "mookie1.com",
    "myads.com",
    "netconversions.com",
    "nexac.com",
    "nextaction.net",
    "nielsen-online.com",
    "offermatica.com",
    "omniture.com",
    "omtrdc.net",
    "pm14.com",
    "quantcast.com",
    "quantserve.com",
    "realmedia.com",
    "revsci.net",
    "rightmedia.com",
    "rmxads.com",
    "ru4.com",
    "rubiconproject.com",
    "samsungadhub.com",
    "scorecardresearch.com",
    "sharethis.com",
    "shopthetv.com",
    "targetingmarketplace.com",
    "themig.com",
    "trendnetcloud.com",
    "yieldmanager.com",
    "yieldmanager.net",
    "yldmgrimg.net",
    "youknowbest.com",
    "yumenetworks.com",
]

# Some additions from myself.  These are based on ads that I've seen myself
# and domains that often occur in the someonewhocares blocklist.
ads += [
    "adengage.com",
    "admob.com",
    "adscience.nl",
    "adtech.de",
    "adtech.fr",
    "adtech.us",
    "am15.net",
    "checkm8.com",
    "cnzz.com",
    "fastclick.net",
    "oewabox.at",
    "p2l.info",
    "petrovka.info",
    "runative-syndicate.com",
    "sitemeter.com",
]


# Remove doubles, sort the list.
ads = sorted(set(ads))

print("#### DNSMASQ ####")
for kind, name in ((facebook, "facebook"), (ads, "ads")):
    print(f"# Block {name}")
    for domain in kind:
        print(f"address=/{domain}/")
    print()

print("#### UNBOUND ####")
print("server:")
for kind, name in ((facebook, "facebook"), (ads, "ads")):
    print(f"    # Block {name}")
    for domain in kind:
        print(f'    local-zone: "{domain}" always_nxdomain')
    print()
