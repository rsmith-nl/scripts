#!/usr/bin/env python3
# file: unlock-excel.pyw
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2020 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2020-03-10T23:06:38+0100
# Last modified: 2020-04-20T00:50:10+0200
"""Remove passwords from modern excel 2007+ files (xlsx, xlsm)."""

from types import SimpleNamespace
import os
import re
import shutil
import stat
import sys
import zipfile

from tkinter import filedialog
from tkinter import ttk
from tkinter.font import nametofont
import tkinter as tk


__version__ = "2020.04.20"


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
    root.bind_all('q', do_exit)
    root.wm_title('Unlock excel files v' + __version__)
    root.columnconfigure(3, weight=1)
    root.rowconfigure(5, weight=1)
    # A SimpleNamespace is used to save widgets that need to be accessed later.
    w = SimpleNamespace()
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
    w.backup = backup
    ttk.Checkbutton(root, text='backup', variable=backup,
                    command=on_backup).grid(row=1, column=1, sticky='ew')
    suffixlabel = ttk.Label(root, text='suffix:')
    suffixlabel['state'] = 'disabled'
    suffixlabel.grid(row=1, column=2, sticky='ew')
    w.suffixlabel = suffixlabel
    suffix = tk.StringVar()
    suffix.set('-orig')
    w.suffix = suffix
    se = ttk.Entry(root, justify='left', textvariable=suffix)
    se.grid(row=1, column=3, columnspan=1, sticky='w')
    se['state'] = 'disabled'
    w.suffixentry = se
    # Third row
    ttk.Label(root, text='(3)').grid(row=2, column=0, sticky='ew')
    gobtn = ttk.Button(root, text="Go!", command=do_start)
    gobtn['state'] = 'disabled'
    gobtn.grid(row=2, column=1, sticky='ew')
    w.gobtn = gobtn
    # Fourth row
    ttk.Label(root, text='(4)').grid(row=3, column=0, sticky='ew')
    ttk.Label(root, text='Progress:').grid(row=3, column=1, sticky='w')
    # Fifth row
    sb = tk.Scrollbar(root, orient="vertical")
    status = tk.Listbox(root, width=40, yscrollcommand=sb.set)
    status.grid(row=4, rowspan=5, column=1, columnspan=3, sticky="nsew")
    w.status = status
    sb.grid(row=4, rowspan=5, column=5, sticky="ns")
    sb.config(command=status.yview)
    # Ninth row
    ttk.Button(root, text="Quit", command=do_exit).grid(row=9, column=1, sticky='ew')
    # Return the widgets that need to be accessed.
    return w


def create_state():
    """Create and initialize the global state."""
    state = SimpleNamespace()
    state.interval = 10
    state.path = ''
    state.inzf, state.outzf = None, None
    state.infos = None
    state.currinfo = None
    state.worksheets_unlocked = 0
    state.workbook_unlocked = False
    state.directory = None
    state.remove = None
    return state


def statusmsg(text):
    """Append a message to the status listbox, and make sure it is visible."""
    widgets.status.insert(tk.END, text)
    widgets.status.see(tk.END)


# Step functions to call in the after() method.
def step_open_zipfiles():
    path = widgets.fn['text']
    state.path = path
    statusmsg(f'Opening “{path}”...')
    first, last = path.rsplit('.', maxsplit=1)
    if widgets.backup.get():
        backupname = first + widgets.suffix.get() + '.' + last
    else:
        backupname = first + '-orig' + '.' + last
        state.remove = backupname
    shutil.move(path, backupname)
    state.inzf = zipfile.ZipFile(backupname, mode="r")
    state.outzf = zipfile.ZipFile(
        path, mode="w", compression=zipfile.ZIP_DEFLATED, compresslevel=1
    )
    root.after(state.interval, step_discover_internal_files)


def step_discover_internal_files():
    statusmsg(f'Reading “{state.path}”...')
    state.infos = [name for name in state.inzf.infolist()]
    state.currinfo = 0
    statusmsg(f'“{state.path}” contains {len(state.infos)} internal files.')
    root.after(state.interval, step_filter_internal_file)


def step_filter_internal_file():
    current = state.infos[state.currinfo]
    stat = f'Processing “{current.filename}” ({state.currinfo+1}/{len(state.infos)})...'
    statusmsg(stat)
    # Doing the actual work
    regex = None
    data = state.inzf.read(current)
    if b'sheetProtect' in data:
        regex = r'<sheetProtect.*?/>'
        statusmsg(f'Worksheet "{current.filename}" is protected.')
    elif b'workbookProtect' in data:
        regex = r'<workbookProtect.*?/>'
        statusmsg('The workbook is protected')
    else:
        state.outzf.writestr(current, data)
    if regex:
        text = data.decode('utf-8')
        newtext = re.sub(regex, '', text)
        if len(newtext) != len(text):
            state.outzf.writestr(current, newtext)
            state.worksheets_unlocked += 1
            statusmsg(f'Removed password from "{current.filename}".')
    # Next iteration or next step.
    state.currinfo += 1
    if state.currinfo >= len(state.infos):
        statusmsg('All internal files processed.')
        state.currinfo = None
        root.after(state.interval, step_close_zipfiles)
    else:
        root.after(state.interval, step_filter_internal_file)


def step_close_zipfiles():
    statusmsg(f'Writing “{state.path}”...')
    state.inzf.close()
    state.outzf.close()
    state.inzf, state.outzf = None, None
    root.after(state.interval, step_finished)


def step_finished():
    if state.remove:
        os.chmod(state.remove, stat.S_IWRITE)
        os.remove(state.remove)
        state.remove = None
    else:
        statusmsg('Removing temporary file')
    statusmsg(f'Unlocked {state.worksheets_unlocked} worksheets.')
    statusmsg('Finished!')
    widgets.gobtn['state'] = 'disabled'
    widgets.fn['text'] = ''
    state.path = ''


# Widget callbacks
def do_file():
    """Callback to open a file"""
    if not state.directory:
        state.directory = ''
        available = [os.environ[k] for k in ('HOME', 'HOMEDRIVE') if k in os.environ]
        if available:
            state.directory = available[0]
    fn = filedialog.askopenfilename(
        title='Excel file to open',
        parent=root,
        defaultextension='.xlsx',
        filetypes=(
            ('excel files', '*.xls*'), ('all files', '*.*')
        ),
    )
    if not fn:
        return
    state.directory = os.path.dirname(fn)
    state.worksheets_unlocked = 0
    state.workbook_unlocked = False
    state.path = fn
    widgets.fn['text'] = fn
    widgets.gobtn['state'] = 'enabled'
    widgets.status.delete(0, tk.END)


def on_backup():
    if widgets.backup.get() == 1:
        widgets.suffixlabel['state'] = 'enabled'
        widgets.suffixentry['state'] = 'enabled'
    else:
        widgets.suffixlabel['state'] = 'disabled'
        widgets.suffixentry['state'] = 'disabled'


def do_start():
    root.after(state.interval, step_open_zipfiles)


def do_exit(arg=None):
    """
    Callback to handle quitting.
    """
    root.destroy()


if __name__ == '__main__':
    # Detach from the command line on UNIX systems.
    if os.name == 'posix':
        if os.fork():
            sys.exit()    # Create the GUI window.
    root = tk.Tk(None)
    # Use a dialog window so that it floats even when using a tiling window
    # manager.
    root.attributes('-type', 'dialog')
    # Don't show hidden files in the file dialog
    # https://stackoverflow.com/questions/53220711/how-to-avoid-hidden-files-in-file-picker-using-tkinter-filedialog-askopenfilenam
    try:
        # call a dummy dialog with an impossible option to initialize the file
        # dialog without really getting a dialog window; this will throw a
        # TclError, so we need a try...except :
        try:
            root.tk.call('tk_getOpenFile', '-foobarbaz')
        except tk.TclError:
            pass
        # now set the magic variables accordingly
        root.tk.call('set', '::tk::dialog::file::showHiddenBtn', '1')
        root.tk.call('set', '::tk::dialog::file::showHiddenVar', '0')
    except Exception:
        pass
    # Widgets is a namespace of widgets that needs to be accessed by the callbacks.
    # State is a namespace of the global state.
    widgets = create_widgets(root)
    state = create_state()
    root.mainloop()
