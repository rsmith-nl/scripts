#!/usr/bin/env python
# file: set-ornata-chroma-rgb.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2019 R.F. Smith <rsmith@xs4all.nl>
# SPDX-License-Identifier: MIT
# Created: 2019-06-16T19:09:06+0200
# Last modified: 2024-03-22T16:20:03+0100
"""Set the LEDs on a Razer Ornata Chroma keyboard to a static RGB color
and / or change the brightness."""

import argparse
import array
import logging
import sys
import usb.core

__version__ = "2024.03.22"


def main():
    """
    Entry point for set-ornata-chroma-rgb.py.
    """
    args = setup()
    color = True
    if args.red == 0 and args.green == 0 and args.blue == 0:
        logging.debug("no color change requested")
        color = False
        if args.brightness == -1:
            logging.debug("also no brightness change requested")
            logging.debug("exiting")
            sys.exit(0)
    dev = usb.core.find(idVendor=0x1532, idProduct=0x021E)
    if dev is None:
        logging.error("no Razer Ornata Chroma keyboard found")
        sys.exit(1)
    logging.debug(str(dev))
    if color:
        logging.info("trying to set the color")
        msg = static_color_msg(args.red, args.green, args.blue)
        logging.info(f"red={args.red}")
        logging.info(f"green={args.green}")
        logging.info(f"blue={args.blue}")
        logging.debug(f"message={msg}")
        read = dev.ctrl_transfer(0x21, 0x09, 0x300, 0x01, msg)
        if read != 90:
            logging.error("control transfer for setting the color failed")
    if args.brightness != -1:
        logging.info("trying to set the brightness")
        msg = brightness_message(args.brightness)
        logging.info(f"brightness={args.brightness}")
        logging.debug(f"message={msg}")
        read = dev.ctrl_transfer(0x21, 0x09, 0x300, 0x01, msg)
        if read != 90:
            logging.error("control transfer for setting the brightness failed")


def setup():
    """Process command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--log",
        default="warning",
        choices=["debug", "info", "warning", "error"],
        help="logging level (defaults to 'warning')",
    )
    parser.add_argument("-v", "--version", action="version", version=__version__)
    parser.add_argument("-i", "--brightness", help="brightness value 0-255", default=-1)
    parser.add_argument("-r", "--red", help="red value 0-255, default 0", default=0)
    parser.add_argument("-g", "--green", help="green value 0-255, default 0", default=0)
    parser.add_argument("-b", "--blue", help="blue value 0-255, default 0", default=0)
    args = parser.parse_args(sys.argv[1:])
    logging.basicConfig(
        level=getattr(logging, args.log.upper(), None),
        format="%(levelname)s: %(message)s",
    )
    logging.debug(f"command line arguments = {sys.argv}")
    logging.debug(f"parsed arguments = {args}")
    return args


def _chk(name, value):
    """
    Check that a value is an integer in the range 0 - 255.
    Log an error and exit when this is not the case.

    Otherwise returns the integer value.
    """
    try:
        if (
            isinstance(value, str)
            and len(value) > 2
            and value[0] == "0"
            and value[1] in "bBoOxX"
        ):
            # Decode binary, octal and hexadecimal numbers.
            value = int(value, {"b": 2, "o": 8, "x": 16}[value[1].lower()])
        else:
            value = int(value)
        if value < 0 or value > 255:
            raise ValueError
    except ValueError:
        logging.error(f"{name} value should be an integer in the range 0 to 255")
        # There is no point continuing with an invalid input
        # *in this case* of a command-line script.
        sys.exit(2)
    return value


def static_color_msg(red, green, blue):
    """
    Create a message to set the Razer Ornata Chroma lights to a static color.
    All arguments should convert to an integer in the range 0-255.

    Returns a bytes object containing the message ready to feed into a ctrl_transfer.
    """
    red, green, blue = _chk("red", red), _chk("green", green), _chk("blue", blue)
    msg = array.array("B", b"\x00" * 90)
    # msg[0] = status = 0
    msg[1] = 0x3F  # transaction id
    # msg[2:4] = remaining packets = 0, 0
    # msg[4] =  protocol type = 0
    msg[5] = 0x09  # data_size
    msg[6] = 0x0F  # command class
    msg[7] = 0x02  # command id
    msg[8] = 0x01  # VARSTORE
    msg[9] = 0x05  # BACKLIGHT_LED
    msg[10] = 0x01  # effect id
    # msg[11:13] are 0
    msg[13] = 0x01  # unknown
    msg[14] = int(red)  # color: red
    msg[15] = int(green)  # color: green
    msg[16] = int(blue)  # color: blue
    chksum = 0
    for j in msg[2:-2]:
        chksum ^= j
    msg[88] = chksum
    return bytes(msg)


def brightness_message(brightness):
    """
    Create a message that sets the brightness on a Razer Ornata Chroma

    Returns an bytes object containing the message ready to feed into a ctrl_transfer.
    """
    brightness = _chk("brightness", brightness)

    msg = array.array("B", b"\x00" * 90)
    # msg[0] = status = 0
    msg[1] = 0x3F  # transaction id
    # msg[2:4] = remaining packets = 0, 0
    # msg[4] =  protocol type = 0
    msg[5] = 0x03  # data_size
    msg[6] = 0x0F  # command class
    msg[7] = 0x04  # command id
    msg[8] = 0x01  # VARSTORE
    msg[9] = 0x05  # BACKLIGHT_LED
    msg[10] = brightness
    chksum = 0
    for j in msg[2:-2]:  # Calculate checksum
        chksum ^= j
    msg[88] = chksum  # Add checksum in penultimate byte
    return bytes(msg)


if __name__ == "__main__":
    main()
