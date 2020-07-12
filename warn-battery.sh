#!/bin/sh
# file: warn-battery.sh
# Script to sound a warning when the battery becomes low. To be run from cron.
# Requires the audio/mpg123 package.
#
# vim:fileencoding=utf-8:fdm=marker:ft=sh
#
# Copyright © 2020 R.F. Smith <rsmith@xs4all.nl>
# Created: 2020-07-12T13:53:59+0200
# Last modified: 2020-07-12T14:19:02+0200


# Get the battery percentage
BAT=`sysctl -n hw.acpi.battery.life`
# Get current sound volume
VOL=`mixer vol | sed -e 's/^.*://'`
if [ $BAT -le 10 ]; then
    # Set sound level and play sound
    mixer vol 50 >/dev/null
    out123 --wave-freq 400 --wave-sweep 800 --sweep-count 5 --wave-pat square
    # Restore sound volume.
    mixer vol $VOL >/dev/null
fi
