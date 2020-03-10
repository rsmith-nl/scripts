# file: unlock-excel.pyw
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2020 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2020-03-10T23:06:38+0100
# Last modified: 2020-03-11T00:47:28+0100
"""Remove passwords from modern excel 2007+ files (xlsx, xlsm)."""

from types import SimpleNamespace

import tkinter as tk
from tkinter import ttk
from tkinter.font import nametofont

__version__ = '0.1'


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
    root.wm_title('Unlock excel files v' + __version__)
    root.columnconfigure(4, weight=1)
    root.rowconfigure(7, weight=1)
    # A SimpleNamespace is used to save widgets that need to be accessed later.
    w = SimpleNamespace()
    # Another is used to hold the state associated with the widgets.
    state = SimpleNamespace()
    # First row
    ttk.Label(root, text='(1)').grid(row=0, column=0, sticky='ew')
    fb = ttk.Button(root, text="Select file", command=do_file)
    fb.grid(row=0, column=1, columnspan=2, sticky="w")
    w.fb = fb
    fn = ttk.Label(root)
    fn.grid(row=0, column=3, columnspan=2, sticky="ew")
    w.fn = fn
    # Second row
    ttk.Label(root, text='(2)').grid(row=1, column=0, sticky='ew')
    backup = tk.IntVar()
    backup.set(0)
    state.backup = backup
    ttk.Checkbutton(root, text='backup', variable=backup,
                    command=on_backup).grid(row=1, column=1, sticky='ew')
    suffixlabel = ttk.Label(root, text='suffix:')
    suffixlabel['state'] = 'disabled'
    suffixlabel.grid(row=1, column=2, sticky='ew')
    w.suffixlabel = suffixlabel
    suffix = tk.StringVar()
    suffix.set('-orig')
    state.suffix = suffix
    se = ttk.Entry(root, justify='left', textvariable=suffix)
    se.grid(row=1, column=3, columnspan=2, sticky='ew')
    se['state'] = 'disabled'
    w.suffixentry = se
    # Third row
    ttk.Label(root, text='(3)').grid(row=2, column=0, sticky='ew')
    start = ttk.Button(root, text="Go!", command=do_start)
    start.grid(row=2, column=1, sticky='ew')
    ttk.Label(root, text='status:').grid(row=2, column=2, sticky='ew')
    status = ttk.Label(root, text='not running')
    status.grid(row=2, column=3, columnspan=4, sticky='ew')
    w.status = status
    # Fourth row
    ttk.Label(root, text='(4)').grid(row=3, column=0, sticky='ew')
    ttk.Label(root, text='Results:').grid(row=3, column=1, sticky='w')
    # Fifth row
    res1 = ttk.Label(root, text='-')
    res1.grid(row=4, column=1, columnspan=4, sticky='ew')
    w.res1 = res1
    # Sixth row
    res2 = ttk.Label(root, text='-')
    res2.grid(row=5, column=1, columnspan=4, sticky='ew')
    w.res2 = res2
    # Seventh row
    ttk.Button(root, text="Quit", command=do_exit).grid(row=6, column=1, sticky='ew')
    # Return the widgets that need to be accessed.
    return w, state


def init_state(s):
    """Initialize the global state."""
    s.interval = 100
    s.inzf = None
    s.outzf = None
    s.files = None
    s.currfile = None
    s.worksheets_total = -1
    s.worksheets_unlocked = 0
    s.workbook_unlocked = False


# Step functions to call in the after() method.
def step_open_zipfiles():
    widgets.status['text'] = 'opening files...'
    root.after(state.interval, step_read_internal_file)


def step_read_internal_file():
    widgets.status['text'] = 'reading...'
    root.after(state.interval, step_filter_internal_file)


def step_filter_internal_file():
    widgets.status['text'] = 'filtering...'
    root.after(state.interval, step_write_internal_file)


def step_write_internal_file():
    widgets.status['text'] = 'writing...'
    root.after(state.interval, step_finished)


def step_finished():
    widgets.status['text'] = 'finished!'


# Widget callbacks
def do_file():
    """Callback to open a file"""
    pass


def on_backup():
    if state.backup.get() == 1:
        widgets.suffixlabel['state'] = 'enabled'
        widgets.suffixentry['state'] = 'enabled'
    else:
        widgets.suffixlabel['state'] = 'disabled'
        widgets.suffixentry['state'] = 'disabled'


def do_start():
    root.after(state.interval, step_open_zipfiles)


def do_exit():
    """
    Callback to handle quitting.
    """
    root.destroy()


def do_q(arg):
    root.destroy()


def step():
    pass


if __name__ == '__main__':
    # Create the GUI window.
    root = tk.Tk(None)
    # widgets is a namespace of widgets that needs to be accessed by the callbacks.
    # state is a namespace of the global state.
    widgets, state = create_widgets(root)
    init_state(state)
    root.mainloop()
