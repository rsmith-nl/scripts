#!/usr/bin/env python3
# file: set-ornata-chroma-rgb.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2019 R.F. Smith <rsmith@xs4all.nl>
# Created: 2019-06-16T19:09:06+0200
# Last modified: 2019-06-16T20:47:20+0200
"""Set the LEDs on a Razer Ornata Chroma keyboard to a static RGB color."""

import argparse
import logging
import sys
import usb.core

__version__ = '0.1'


def static_color_msg(red, green, blue):
    """
    Create a message to set the Razer Ornata Croma lights to a static color.
    All arguments should be convertable to an integer in the range 0-255.

    Returns a bytearray containing the message.
    """

    def _chk(name, channel):
        if (
            isinstance(channel, str) and len(channel) > 2 and channel[0] == '0' and
            channel[1] in 'bBoOxX'
        ):
            channel = int(channel, {'b': 2, 'o': 8, 'x': 16}[channel[1].lower()])
        else:
            channel = int(channel)
        if channel < 0 or channel > 255:
            logging.error(f'{name} value should be in the range 0 to 255')
            sys.exit(2)
        return channel

    red = _chk('red', red)
    green = _chk('green', green)
    blue = _chk('blue', blue)
    msg = bytearray(90)
    # byte 0 is 0
    msg[1] = 0x3F  # transaction id
    # bytes 2-4 are 0.
    msg[5] = 0x09  # data size
    msg[6] = 0x0F  # command class
    msg[7] = 0x02  # command id
    # The rest of the msg bytes are variable data
    msg[8] = 0x01  # VARSTORE
    msg[9] = 0x05  # BACKLIGHT_LED
    msg[10] = 0x01  # effect id
    # bytes 11-12 are 0.
    msg[13] = 0x01
    msg[14] = red
    msg[15] = green
    msg[16] = blue
    # Calculate and set the checksum.
    crc = 0
    for j in msg[2:88]:
        crc ^= j
    msg[-2] = crc
    return msg


def main(argv):
    """
    Entry point for set-ornata-chroma-rgb.py.

    Arguments:
        argv: command line arguments
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--log',
        default='warning',
        choices=['debug', 'info', 'warning', 'error'],
        help="logging level (defaults to 'warning')"
    )
    parser.add_argument('-v', '--version', action='version', version=__version__)
    parser.add_argument('red', help="red value 0-255")
    parser.add_argument('green', help="green value 0-255")
    parser.add_argument('blue', help="blue value 0-255")
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log.upper(), None),
        format='%(levelname)s: %(message)s'
    )
    logging.debug(f'command line arguments = {argv}')
    logging.debug(f'parsed arguments = {args}')

    dev = usb.core.find(idVendor=0x1532, idProduct=0x021e)
    if dev is None:
        logging.error('No Razer Ornata Chroma keyboard found')
        sys.exit(1)
    msg = static_color_msg(args.red, args.green, args.blue)  # set color to Green.
    logging.info(f'red={args.red}')
    logging.info(f'green={args.green}')
    logging.info(f'blue={args.blue}')
    read = dev.ctrl_transfer(0x21, 0x09, 0x300, 0x01, msg)
    if read != 90:
        logging.error('control transfer for setting the color failed')


if __name__ == '__main__':
    main(sys.argv[1:])
