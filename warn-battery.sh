#!/bin/sh
# file: warn-battery.sh
# Script to sound a warning when the battery becomes low. To be run from cron.
# Requires the audio/mpg123 package.
#
# vim:fileencoding=utf-8:fdm=marker:ft=sh
#
# Copyright © 2020 R.F. Smith <rsmith@xs4all.nl>
# SPDX-License-Identifier: MIT
# Created: 2020-07-12T13:53:59+0200
# Last modified: 2021-02-28T20:48:30+0100

set -e

# Locations of binaries.
MIXER=/usr/sbin/mixer
OUT=/usr/local/bin/out123

# Get the battery percentage and state
BAT=`sysctl -n hw.acpi.battery.life`
STATE=`sysctl -n hw.acpi.battery.state`
# Get current sound volume
VOL=`mixer vol | sed -e 's/^.*://'`
if [ $STATE -eq 1 -a $BAT -le 10 ]; then
    # Set sound level and play sound
    $MIXER vol 50 >/dev/null
    $OUT --wave-freq 400 --wave-sweep 800 --sweep-count 5 --wave-pat square
    # Restore sound volume.
    $MIXER vol $VOL >/dev/null
fi
