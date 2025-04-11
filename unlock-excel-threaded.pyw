#!/usr/bin/env python
# file: unlock-excel-threaded.pyw
# vim:fileencoding=utf-8:ft=python
#
# Copyright © 2020 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2020-03-10T23:06:38+0100
# Last modified: 2025-04-11T22:48:55+0200
"""Remove passwords from modern excel 2007+ files (xlsx, xlsm).

This is a multithreaded version of unlock-excel.pyw.  All the work that was
there done in steps in the mainloop is now done in a single additional thread.

There is some confusion whether tkinter is thread-safe.  That is, if one can
call tkinter functions and methods from any but the main thread.  The
documentation for Python 3 says “yes”.  Comments in the C source code for
tkinter say “its complicated” depending on how tcl is built.  *Many* online
sources say “no”, but that could just be an echo chamber effect.

The author has tested this code on FreeBSD 12.1-STABLE amd64 using CPython
3.7.7 combined with a tcl built with threading enabled.  There at least it
seems to work without problems.
"""

from types import SimpleNamespace
import os
import re
import shutil
import stat
import sys
import threading
import zipfile

from tkinter import filedialog
from tkinter import ttk
from tkinter.font import nametofont
import tkinter as tk

__version__ = "2025.04.11"
widgets = SimpleNamespace()
state = SimpleNamespace()


def create_widgets(root, w):
    """Create the window and its widgets.

    Arguments:
        root: the root window.
        w: SimpleNamespace to store widgets.
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
    # First row
    ttk.Label(root, text='(1)').grid(row=0, column=0, sticky='ew')
    w.fb = ttk.Button(root, text="Select file", command=do_file)
    w.fb.grid(row=0, column=1, columnspan=2, sticky="w")
    w.fn = ttk.Label(root)
    w.fn.grid(row=0, column=3, columnspan=2, sticky="ew")
    # Second row
    ttk.Label(root, text='(2)').grid(row=1, column=0, sticky='ew')
    w.backup = tk.IntVar()
    w.backup.set(0)
    ttk.Checkbutton(root, text='backup', variable=w.backup,
                    command=on_backup).grid(row=1, column=1, sticky='ew')
    w.suffixlabel = ttk.Label(root, text='suffix:', state=tk.DISABLED)
    w.suffixlabel.grid(row=1, column=2, sticky='ew')
    w.suffix = tk.StringVar()
    w.suffix.set('-orig')
    se = ttk.Entry(root, justify='left', textvariable=w.suffix, state=tk.DISABLED)
    se.grid(row=1, column=3, columnspan=1, sticky='w')
    w.suffixentry = se
    # Third row
    ttk.Label(root, text='(3)').grid(row=2, column=0, sticky='ew')
    w.gobtn = ttk.Button(root, text="Go!", command=do_start, state=tk.DISABLED)
    w.gobtn.grid(row=2, column=1, sticky='ew')
    # Fourth row
    ttk.Label(root, text='(4)').grid(row=3, column=0, sticky='ew')
    ttk.Label(root, text='Progress:').grid(row=3, column=1, sticky='w')
    # Fifth row
    sb = tk.Scrollbar(root, orient="vertical")
    w.status = tk.Listbox(root, width=60, yscrollcommand=sb.set)
    w.status.grid(row=4, rowspan=5, column=1, columnspan=3, sticky="nsew")
    sb.grid(row=4, rowspan=5, column=5, sticky="ns")
    sb.config(command=w.status.yview)
    # Ninth row
    ttk.Button(root, text="Quit", command=do_exit).grid(row=9, column=1, sticky='ew')


def initialize_state(s):
    """
    Initialize the global state.

    Arguments:
        s: SimpleNamespace to store application state.
    """
    s.directory = None


def statusmsg(text):
    """Append a message to the status listbox, and make sure it is visible."""
    widgets.status.insert(tk.END, text)
    widgets.status.see(tk.END)


def process_zipfile_thread():
    """Function to process a zip-file. This is to be run in a thread."""
    path = widgets.fn['text']
    statusmsg(f'Opening “{path}”...')
    first, last = path.rsplit('.', maxsplit=1)
    if widgets.backup.get():
        backupname = first + widgets.suffix.get() + '.' + last
        remove = None
    else:
        backupname = first + '-orig' + '.' + last
        remove = backupname
    shutil.move(path, backupname)
    with zipfile.ZipFile(backupname, mode="r") as inzf, \
            zipfile.ZipFile(
                path, mode="w", compression=zipfile.ZIP_DEFLATED, compresslevel=1
            ) as outzf:
        statusmsg(f'Reading “{path}”...')
        infos = [name for name in inzf.infolist()]
        statusmsg(f'“{path}” contains {len(infos)} internal files.')
        worksheets_unlocked = 0
        for idx, current in enumerate(infos, start=1):
            smsg = f'Processing “{current.filename}” ({idx}/{len(infos)})...'
            statusmsg(smsg)
            # Doing the actual work
            regex = None
            data = inzf.read(current)
            if b'sheetProtect' in data:
                regex = r'<sheetProtect.*?/>'
                statusmsg(f'Worksheet "{current.filename}" is protected.')
            elif b'workbookProtect' in data:
                regex = r'<workbookProtect.*?/>'
                statusmsg('The workbook is protected')
            else:
                outzf.writestr(current, data)
            if regex:
                text = data.decode('utf-8')
                newtext = re.sub(regex, '', text)
                if len(newtext) != len(text):
                    outzf.writestr(current, newtext)
                    if 'sheet' in regex:
                        state.worksheets_unlocked += 1
                        statusmsg(f'Removed password from "{current.filename}".')
                    elif 'workbook' in regex:
                        state.workbook_unlocked = True
    statusmsg('All internal files processed.')
    statusmsg(f'Writing “{path}”...')
    if remove:
        os.chmod(remove, stat.S_IWRITE)
        os.remove(remove)
    else:
        statusmsg('Removing temporary file')
    statusmsg(f'Unlocked {worksheets_unlocked} worksheets.')
    if state.workbook_unlocked:
        statusmsg(f'Removed password from workbook {state.path}.')
    statusmsg('Finished!')
    widgets.gobtn['state'] = 'disabled'
    widgets.fn['text'] = ''


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
        filetypes=(('excel files', '*.xls*'), ('all files', '*.*')),
    )
    if not fn:
        return
    state.directory = os.path.dirname(fn)
    state.workbook_unlocked = False
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
    worker = threading.Thread(target=process_zipfile_thread)
    worker.start()


def do_exit(arg=None):
    """
    Callback to handle quitting.
    """
    root.destroy()


if __name__ == '__main__':
    # Detach from the command line on UNIX systems.
    if os.name == 'posix':
        if os.fork():
            sys.exit()
    # Create the GUI window.
    root = tk.Tk(None)
    # Use a dialog window so that it floats even when using a tiling window manager.
    if os.name == 'posix':
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
    create_widgets(root, widgets)
    initialize_state(state)
    root.mainloop()
