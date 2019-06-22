#!/usr/bin/env python3
# file: set-ornata-chroma-rgb.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2019 R.F. Smith <rsmith@xs4all.nl>
# SPDX-License-Identifier: MIT
# Created: 2019-06-16T19:09:06+0200
# Last modified: 2019-06-22T19:43:10+0200
"""Set the LEDs on a Razer Ornata Chroma keyboard to a static RGB color."""

import array
import argparse
import logging
import sys
import usb.core

__version__ = '0.2'


def static_color_msg(red, green, blue):
    """
    Create a message to set the Razer Ornata Croma lights to a static color.
    All arguments should convert to an integer in the range 0-255.

    Returns an array.array containing the message ready to feed into a ctrl_transfer.
    """

    def _chk(name, channel):
        if (
            isinstance(channel, str) and len(channel) > 2 and channel[0] == '0' and
            channel[1] in 'bBoOxX'
        ):
            # Decode binary, octal and hexadecimal numbers.
            channel = int(channel, {'b': 2, 'o': 8, 'x': 16}[channel[1].lower()])
        else:
            channel = int(channel)
        if channel < 0 or channel > 255:
            logging.error(f'{name} value should be in the range 0 to 255')
            # There is no point continuing with an invalid input
            # *in this case* of a command-line script.
            sys.exit(2)
        return channel
    red, green, blue = _chk('red', red), _chk('green', green), _chk('blue', blue)

    # Meaning of the nonzero bytes, in sequence:
    # 0x3f = transaction id, 0x09 = variable data length, 0x0f = command class,
    # 0x02 = command id, 0x01 = VARSTORE, 0x05 = BACKLIGHT_LED, 0x01 = effect id,
    # 0x01 =  unknown
    msg = array.array('B', b'\x00\x3f\x00\x00\x00\x09\x0f\x02\x01\x05\x01\x00\x00\x01')
    msg.extend([red, green, blue])
    crc = 0
    for j in msg[2:]:
        crc ^= j
    msg.extend(bytes(71))
    msg.extend([crc, 0])
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
    logging.debug(str(dev))
    msg = static_color_msg(args.red, args.green, args.blue)
    logging.info(f'red={args.red}')
    logging.info(f'green={args.green}')
    logging.info(f'blue={args.blue}')
    logging.debug(f'message={msg}')
    read = dev.ctrl_transfer(0x21, 0x09, 0x300, 0x01, msg)
    if read != 90:
        logging.error('control transfer for setting the color failed')


if __name__ == '__main__':
    main(sys.argv[1:])
