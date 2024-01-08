#!/usr/bin/env python3
"""DownLoad FrontEnd

A GUI for yt-dlp that allows to easily select options.
"""

from types import SimpleNamespace
import os
import sys

import tkinter as tk
from tkinter import ttk
from tkinter.font import nametofont

__version__ = "2024.01.07"
# Namespace for widgets that need to be accessed by callbacks.
w = SimpleNamespace()
# State that needs to be accessed by callbacks.
state = SimpleNamespace()


def create_widgets(root, w):
    """Create the window and its widgets.

    Arguments:
        root: the root window.
        w: SimpleNamespace where widgets can be added to.
    """
    # Set the font.
    default_font = nametofont("TkDefaultFont")
    default_font.configure(size=12)
    root.option_add("*Font", default_font)
    # General commands and bindings
    root.wm_title("DownLoad FrontEnd v" + __version__)
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=1)
    root.rowconfigure(0, weight=1)
    root.rowconfigure(1, weight=1)
    root.rowconfigure(2, weight=1)
    root.bind("q", do_exit)
    # First row
    ttk.Label(root, text="URL:").grid(row=0, column=0, sticky="w")
    state.urlentry = tk.StringVar()
    ttk.Entry(root, textvariable=state.urlentry).grid(row=0, column=1, sticky="ew")
    # Second row
    ttk.Label(root, text="Resolution (vertical):").grid(row=1, column=0, sticky="w")
    state.resolution = tk.StringVar(value="720")
    w.resolution = ttk.Combobox(root, textvariable=state.resolution)
    w.resolution.grid(row=1, column=1, sticky="ew")
    w.resolution['values'] = (
        '720',
        '1080'
    )
    # Third row
    ttk.Label(root, text="Chapters:").grid(row=2, column=0, sticky="w")
    w.chapters = ttk.Checkbutton(root)
    w.chapters.grid(row=2, column=1, sticky="w")
    # Fourth row
    ttk.Label(root, text="Subtitles:").grid(row=3, column=0, sticky="w")
    state.subs = tk.BooleanVar(value=False)
    subs = ttk.Checkbutton(root, command=do_subs_changed, variable=state.subs)
    subs.grid(row=3, column=1, sticky="w")
    # Fifth row
    ttk.Label(root, text="Subtitle language:").grid(row=4, column=0, sticky="w")
    state.sublang = tk.StringVar(value="en")
    w.sublang = ttk.Entry(root, textvariable=state.sublang, state="disabled")
    w.sublang.grid(row=4, column=1, sticky="ew")
    # Sixth row
    # Last row
    q = ttk.Button(root, text="Quit", command=do_exit)
    q.grid(row=5, column=0, sticky="w")
    r = ttk.Button(root, text="Run", command=do_run)
    r.grid(row=5, column=1, sticky="w")


# Callbacks
def do_subs_changed():
    """Enable or disable subtitle language entry box depending on the value
    associated withthe checkbutton for subtitles."""
    if state.subs.get() is True:
        w.sublang["state"] = "enabled"
    else:
        w.sublang["state"] = "disabled"


def do_run():
    pass


def do_exit(arg=None):
    root.destroy()


# Helper functions


# Program starts here.
if __name__ == "__main__":
    # Detach from the command line on UNIX systems.
    if os.name == "posix":
        if os.fork():
            sys.exit()
    # Initialize global state
    state.red, state.green, state.blue = 0, 0, 0
    # Create the GUI.
    root = tk.Tk(None)
    if os.name == "posix":
        # Make a floating window even if using a tiling window manager.
        # This “-type” is unknown on ms-windows.
        root.attributes("-type", "dialog")
    create_widgets(root, w)
    root.mainloop()
