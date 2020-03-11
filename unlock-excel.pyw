# file: unlock-excel.pyw
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2020 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2020-03-10T23:06:38+0100
# Last modified: 2020-03-11T22:39:16+0100
"""Remove passwords from modern excel 2007+ files (xlsx, xlsm)."""

from types import SimpleNamespace
import os
import stat
import re
import shutil
import zipfile

import tkinter as tk
from tkinter import ttk
from tkinter.font import nametofont
from tkinter import filedialog


__version__ = '0.2'


def create_widgets(root):
    """Create the window and its widgets.

    Arguments:
        root: the root window.

    Returns:
        A SimpleNamespace of widgets
        A SimpleNamespace of state

    """
    # Set the font.
    default_font = nametofont("TkDefaultFont")
    default_font.configure(size=12)
    root.option_add("*Font", default_font)
    # General commands and bindings
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
    gobtn = ttk.Button(root, text="Go!", command=do_start)
    gobtn['state'] = 'disabled'
    gobtn.grid(row=2, column=1, sticky='ew')
    w.gobtn = gobtn
    ttk.Label(root, text='status:').grid(row=2, column=2, sticky='ew')
    status = ttk.Label(root, text='not running', width=30)
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
    # Return the widgets and state that need to be accessed.
    return w, state


def init_state(state):
    """Initialize the global state."""
    state.interval = 100
    state.path = ''
    state.inzf, state.outzf = None, None
    state.infos = None
    state.currinfo = None
    state.worksheets_unlocked = 0
    state.workbook_unlocked = False
    state.directory = None
    state.remove = None


# Step functions to call in the after() method.
def step_open_zipfiles():
    path = widgets.fn['text']
    state.path = path
    widgets.status['text'] = f'opening “{path}”...'
    first, last = path.rsplit('.', maxsplit=1)
    if state.backup.get():
        backupname = first + state.suffix.get() + '.' + last
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
    widgets.status['text'] = f'reading “{state.path}”...'
    state.infos = [name for name in state.inzf.infolist()]
    state.currinfo = 0
    widgets.status['text'] = f'“{state.path}” contains {len(state.infos)} files.'
    root.after(state.interval, step_filter_internal_file)


def step_filter_internal_file():
    current = state.infos[state.currinfo]
    stat = f'processing “{current.filename}” ({state.currinfo+1}/{len(state.infos)})...'
    widgets.status['text'] = stat
    # Doing the actual work
    regex = None
    data = state.inzf.read(current)
    if b'sheetProtect' in data:
        regex = r'<sheetProtect.*?/>'
        widgets.status['text'] = f'worksheet "{current.filename}" is protected.'
    elif b'workbookProtect' in data:
        regex = r'<workbookProtect.*?/>'
        widgets.res2['text'] = '- workbook unlocked.'
        widgets.status['text'] = 'the workbook is protected'
    else:
        state.outzf.writestr(current, data)
    if regex:
        text = data.decode('utf-8')
        newtext = re.sub(regex, '', text)
        if len(newtext) != len(text):
            state.outzf.writestr(current, newtext)
            state.worksheets_unlocked += 1
            widgets.status['text'] = f'removed password from "{current.filename}".'
    # Next iteration or next step.
    state.currinfo += 1
    if state.currinfo >= len(state.infos):
        widgets.status['text'] = 'all sheets processed.'
        state.currinfo = None
        root.after(state.interval, step_close_zipfiles)
    else:
        root.after(state.interval, step_filter_internal_file)


def step_close_zipfiles():
    widgets.status['text'] = f'writing “{state.path}”...'
    state.inzf.close()
    state.outzf.close()
    state.inzf, state.outzf = None, None
    widgets.res1['text'] = f'- unlocked {state.worksheets_unlocked} worksheets.'
    root.after(state.interval, step_finished)


def step_finished():
    if state.remove:
        widgets.status['text'] = 'removing temporary file'
        os.chmod(state.remove, stat.S_IWRITE)
        os.remove(state.remove)
        state.remove = None
    widgets.status['text'] = 'finished!'
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
            ('excel files', '*.xlsx'), ('excel files with macros', '*.xlsm'),
            ('all files', '*.*')
        ),
        initialdir=state.directory
    )
    if not fn:
        return
    state.directory = os.path.dirname(fn)
    state.worksheets_unlocked = 0
    state.workbook_unlocked = False
    state.path = fn
    widgets.fn['text'] = fn
    widgets.status['text'] = 'not running.'
    widgets.res1['text'] = '-'
    widgets.res2['text'] = '-'
    widgets.gobtn['state'] = 'enabled'


def on_backup():
    if state.backup.get() == 1:
        widgets.suffixlabel['state'] = 'enabled'
        widgets.suffixentry['state'] = 'enabled'
    else:
        widgets.suffixlabel['state'] = 'disabled'
        widgets.suffixentry['state'] = 'disabled'


def do_start():
    root.after(state.interval, step_open_zipfiles)


def do_exit(**args):
    """
    Callback to handle quitting.
    """
    root.destroy()


def step():
    pass


if __name__ == '__main__':
    # Create the GUI window.
    root = tk.Tk(None)
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
    widgets, state = create_widgets(root)
    init_state(state)
    root.mainloop()
