#!/usr/bin/env python3
# file: x-ornata-chroma-rgb.pyw
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2020 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2020-03-14T22:44:16+0100
# Last modified: 2020-03-16T19:23:43+0100
"""Set the LEDs on a Razer Ornata Chroma keyboard to a static RGB color."""

from tkinter import messagebox
from tkinter import ttk
from tkinter.font import nametofont
from types import SimpleNamespace
import os
import sys
import tkinter as tk
import usb.core

__version__ = '1.0'


def create_widgets(root):
    """Create the window and its widgets.

    Arguments:
        root: the root window.

    Returns:
        A SimpleNamespace of widgets

    """
    # Set the font.
    default_font = nametofont("TkDefaultFont")
    default_font.configure(size=12)
    root.option_add("*Font", default_font)
    # General commands and bindings
    root.bind_all('q', do_q)
    root.wm_title('Razer Ornata Chroma color v' + __version__)
    root.columnconfigure(1, weight=1)
    root.rowconfigure(0, weight=1)
    root.rowconfigure(1, weight=1)
    root.rowconfigure(2, weight=1)
    # SimpleNamespace to save widgets that need to be accessed later.
    w = SimpleNamespace()
    # First row
    ttk.Label(root, text='Red').grid(row=0, column=0, sticky='w')
    red = tk.Scale(root, from_=0, to=255, orient=tk.HORIZONTAL, length=255,
                   command=do_red)
    red.grid(row=0, column=1, sticky="nsew")
    w.red = red
    show = tk.Frame(root, width=100, height=100, bg='#000000')
    show.grid(row=0, column=2, rowspan=3)
    w.show = show
    # Second row
    ttk.Label(root, text='Green').grid(row=1, column=0, sticky='w')
    green = tk.Scale(root, from_=0, to=255, orient=tk.HORIZONTAL, length=255,
                     command=do_green)
    green.grid(row=1, column=1, sticky="ew")
    w.green = green
    # Third row
    ttk.Label(root, text='Blue').grid(row=2, column=0, sticky='w')
    blue = tk.Scale(root, from_=0, to=255, orient=tk.HORIZONTAL, length=255,
                    command=do_blue)
    blue.grid(row=2, column=1, sticky="ew")
    w.blue = blue
    # Last row
    b = ttk.Button(root, text="Quit", command=do_exit)
    b.grid(row=3, column=0, sticky='w')
    setkb = ttk.Button(root, text="Set", command=do_set)
    setkb.grid(row=3, column=2, sticky='e')
    # Return the widgets that need to be accessed.
    return w


# Callbacks
def do_q(arg):
    """Handle the q key."""
    root.destroy()


def do_exit():
    """Callback to handle the quit button."""
    root.destroy()


def update_color():
    """Helper function to update the color example."""
    value = f'#{state.red:02x}{state.green:02x}{state.blue:02x}'
    w.show['bg'] = value


def do_red(r):
    """Process movement of the red slider."""
    state.red = int(r)
    update_color()


def do_green(g):
    """Process movement of the green slider."""
    state.green = int(g)
    update_color()


def do_blue(b):
    """Process movement of the blue slider."""
    state.blue = int(b)
    update_color()


def do_set():
    """Callback to set the color on the keyboard."""
    msg = static_color_msg(state.red, state.green, state.blue)
    read = state.dev.ctrl_transfer(0x21, 0x09, 0x300, 0x01, msg)
    if read != 90:
        messagebox.showerror('Set color', 'Operation failed.')


def static_color_msg(red, green, blue):
    """
    Create a message to set the Razer Ornata Chroma lights to a static color.
    All arguments should be an integer in the range 0-255.

    Returns an bytes object containing the message ready to feed into a ctrl_transfer.
    """
    # Meaning of the nonzero bytes, in sequence: 0x3f = transaction id, 0x09
    # = length of used arguments, 0x0f = command class, 0x02 = command id
    hdr = b'\x00\x3f\x00\x00\x00\x09\x0f\x02'
    # Meaning of the nonzero bytes, in sequence: 0x01 = VARSTORE, 0x05
    # = BACKLIGHT_LED, 0x01 = effect id, 0x01 = unknown
    arguments = b'\x01\x05\x01\x00\x00\x01'
    msg = hdr + arguments + bytes([red, green, blue])  # Add color.
    chksum = 0
    for j in msg[2:]:  # Calculate the checksum
        chksum ^= j
    msg += bytes(80 - 9)  # Add filler; the variable message buffer is 80 bytes.
    msg += bytes([chksum, 0])  # Add checksum in penultimate byte
    return msg


if __name__ == '__main__':
    # Detach from the command line on UNIX systems.
    if os.name == 'posix':
        if os.fork():
            sys.exit()
    # Global state
    state = SimpleNamespace()
    state.red, state.green, state.blue = 0, 0, 0
    state.dev = usb.core.find(idVendor=0x1532, idProduct=0x021e)
    # Create the GUI window.
    root = tk.Tk(None)
    if state.dev is not None:
        # w is a namespace of widgets that needs to be accessed by the callbacks.
        w = create_widgets(root)
    else:
        messagebox.showerror('Device detection', 'No Ornata Chroma found')
        root.destroy()
    root.mainloop()
