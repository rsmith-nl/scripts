#!/usr/bin/env python
# file: tk-razer.pyw
# vim:fileencoding=utf-8:ft=python
#
# Copyright © 2020 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2020-03-14T22:44:16+0100
# Last modified: 2023-03-13T23:30:36+0100
"""Set the LEDs on a Razer keyboard to a static RGB color.

Uses the tkinter toolkit that comes with Python.

Tested on an Ornata Chroma and a BlackWidow Elite.
The USB control transfer messages were laboriously extracted from the
Openrazer (https://github.com/openrazer/openrazer) driver code.
"""

from tkinter import messagebox
from tkinter import ttk
from tkinter.font import nametofont
from types import SimpleNamespace
import array
import os
import sys
import tkinter as tk
import usb.core

__version__ = "2023.03.13"


def create_widgets(root, model):
    """Create the window and its widgets.

    Arguments:
        root: the root window.
        model (str): keyboard model

    Returns:
        A SimpleNamespace of widgets

    """
    # Set the font.
    default_font = nametofont("TkDefaultFont")
    default_font.configure(size=12)
    root.option_add("*Font", default_font)
    # General commands and bindings
    root.bind_all('q', do_exit)
    root.wm_title('Razer keyboard color v' + __version__)
    root.columnconfigure(1, weight=1)
    root.rowconfigure(0, weight=1)
    root.rowconfigure(1, weight=1)
    root.rowconfigure(2, weight=1)
    root.rowconfigure(3, weight=1)
    # SimpleNamespace to save widgets that need to be accessed later.
    w = SimpleNamespace()
    # First row
    ttk.Label(root, text=model, anchor=tk.CENTER).grid(row=0, column=0, columnspan=3, sticky='ew')
    # Second row
    ttk.Button(root, text='Red', command=set_red).grid(row=1, column=0, sticky="ew")
    red = tk.Scale(
        root, from_=0, to=255, orient=tk.HORIZONTAL, length=255, command=do_red
    )
    red.grid(row=1, column=1, sticky="nsew")
    w.red = red
    show = tk.Frame(root, width=100, height=100, bg='#000000')
    show.grid(row=1, column=2, rowspan=3)
    w.show = show
    # Third row
    ttk.Button(root, text='Green', command=set_green).grid(row=2, column=0, sticky="ew")
    green = tk.Scale(
        root, from_=0, to=255, orient=tk.HORIZONTAL, length=255, command=do_green
    )
    green.grid(row=2, column=1, sticky="ew")
    w.green = green
    # Fourth row
    ttk.Button(root, text='Blue', command=set_blue).grid(row=3, column=0, sticky="ew")
    blue = tk.Scale(
        root, from_=0, to=255, orient=tk.HORIZONTAL, length=255, command=do_blue
    )
    blue.grid(row=3, column=1, sticky="ew")
    w.blue = blue
    # Last row
    b = ttk.Button(root, text="Close", command=do_exit)
    b.grid(row=4, column=0, sticky='ew')
    setb = ttk.Button(root, text="Set", command=do_set)
    setb.grid(row=4, column=2, sticky='e')
    w.setb = setb
    # Return the widgets that need to be accessed.
    return w


# Callbacks
def do_exit(arg=None):
    """Callback to quit the application."""
    root.destroy()


def update_color():
    """Helper function to update the color example."""
    value = f'#{state.red:02x}{state.green:02x}{state.blue:02x}'
    w.show['bg'] = value


def set_red():
    """Set the color to pure red."""
    w.red.set(255)
    w.green.set(0)
    w.blue.set(0)


def set_green():
    """Set the color to pure green."""
    w.red.set(0)
    w.green.set(255)
    w.blue.set(0)


def set_blue():
    """Set the color to pure blue."""
    w.red.set(0)
    w.green.set(0)
    w.blue.set(255)


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
    w.setb['state'] = tk.DISABLED
    msg = static_color_msg(state.red, state.green, state.blue)
    # 0x21: request_type USB_TYPE_CLASS | USB_RECIP_INTERFACE | USB_DIR_OUT
    # 0x09: request HID_REQ_SET_REPORT
    # 0x300: value
    # 0x01: report index HID_REQ_GET_REPORT
    read = state.dev.ctrl_transfer(0x21, 0x09, 0x300, 0x01, msg)
    if read != 90:
        messagebox.showerror('Set color', 'Operation failed.')
    w.setb['state'] = tk.NORMAL


def static_color_msg(red, green, blue):
    """
    Create a message to set the Razer Ornata Chroma lights to a static color.
    All arguments should be an number in the range 0-255.

    Returns an array object containing the message ready to feed into a ctrl_transfer.
    """
    msg = array.array("B", b'\x00'*90)
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
    return msg


if __name__ == '__main__':
    # Detach from the command line on UNIX systems.
    if os.name == 'posix':
        if os.fork():
            sys.exit()
    # Global state
    state = SimpleNamespace()
    state.red, state.green, state.blue = 0, 0, 0
    state.dev = None
    # Find devices
    devs = list(usb.core.find(find_all=True, idVendor=0x1532))
    if devs:
        state.dev = devs[0]
        state.model = devs[0].product
        state.id = devs[0].idProduct
    # Create the GUI window.
    root = tk.Tk(None)
    # Use a dialog window so that it floats even when using a tiling window
    # manager.
    root.attributes('-type', 'dialog')
    if state.dev is not None:
        # w is a namespace of widgets that needs to be accessed by the callbacks.
        w = create_widgets(root, model=f"{state.model} (0x1532:0x{state.id:04x})")
    else:
        messagebox.showerror('Device detection', 'No Ornata Chroma found')
        root.destroy()
    root.mainloop()
