#!/usr/bin/env python3
"""DownLoad FrontEnd

A GUI for yt-dlp that allows to easily select options.
"""

from types import SimpleNamespace
import os
import sys
import subprocess as sp

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
    root.bind("q", do_exit)
    # Row
    ttk.Label(root, text="URL:").grid(row=0, column=0, sticky="w")
    state.url = tk.StringVar()
    ttk.Entry(root, textvariable=state.url, width=40).grid(row=0, column=1, sticky="ew")
    # Row
    ttk.Label(root, text="Output name:").grid(row=1, column=0, sticky="w")
    state.outname = tk.StringVar()
    ttk.Entry(root, textvariable=state.outname).grid(row=1, column=1, sticky="ew")
    # Row
    ttk.Label(root, text="Output directory:").grid(row=2, column=0, sticky="w")
    state.outdir = tk.StringVar(value="~/tmp")
    ttk.Entry(root, textvariable=state.outdir).grid(row=2, column=1, sticky="ew")
    # Row
    ttk.Label(root, text="Resolution (vertical):").grid(row=3, column=0, sticky="w")
    state.resolution = tk.StringVar(value="720")
    w.resolution = ttk.Combobox(root, textvariable=state.resolution)
    w.resolution.grid(row=3, column=1, sticky="ew")
    w.resolution["values"] = ("720", "1080")
    # Row
    ttk.Label(root, text="Chapters:").grid(row=4, column=0, sticky="w")
    state.chapters = tk.BooleanVar(value=False)
    ttk.Checkbutton(root, variable=state.chapters).grid(row=4, column=1, sticky="w")
    # Row
    ttk.Label(root, text="Subtitles:").grid(row=5, column=0, sticky="w")
    state.subs = tk.BooleanVar(value=False)
    subs = ttk.Checkbutton(root, command=do_subs_changed, variable=state.subs)
    subs.grid(row=5, column=1, sticky="w")
    # Row
    ttk.Label(root, text="Subtitle language:").grid(row=6, column=0, sticky="w")
    state.sublang = tk.StringVar(value="en")
    w.sublang = ttk.Entry(root, textvariable=state.sublang, state="disabled")
    w.sublang.grid(row=6, column=1, sticky="ew")
    # Row
    w.run = ttk.Button(root, text="Run", command=do_run)
    w.run.grid(row=7, column=0, sticky="w")
    w.cancel = ttk.Button(root, text="Cancel", command=do_cancel, state="disabled")
    w.cancel.grid(row=7, column=1, sticky="w")
    # Rows
    ttk.Label(root, text="Downloader output:").grid(row=8, column=0, sticky="w")
    w.text = tk.Text(root, width=40, height=10)
    w.text.grid(row=9, column=0, columnspan=2, sticky="ew")
    # Row
    ttk.Button(root, text="Quit", command=do_exit).grid(row=10, column=0, sticky="w")


# Callbacks
def do_subs_changed():
    """Enable or disable subtitle language entry box depending on the value
    associated withthe checkbutton for subtitles."""
    if state.subs.get() is True:
        w.sublang["state"] = "enabled"
    else:
        w.sublang["state"] = "disabled"


def do_run():
    """Start the download process."""
    w.text.delete("1.0", "end")
    res = state.resolution.get()
    args = ["yt-dlp", "--newline", "-S", f"res:{res}"]
    if state.chapters.get() is True:
        args.append = ["--embed-chapters"]
    if state.subs.get() is True:
        sublang = state.sublang.get()
        args.append = ["--sub-langs", f"{sublang}", "--write-subs", "--embed-subs"]
    url = state.url.get()
    if not url:
        w.text.insert("1.0", "No URL supplied.")
        return
    outdir = state.outdir.get()
    if outdir.startswith("~"):
        outdir = os.environ["HOME"] + outdir[1:]
    outname = state.outname.get()
    tt = {ord(j): "_" for j in ",.;:'|"}
    if outname:
        outname = outname.replace(" - ", "-")
        outname = outname.translate(tt)
        outname = outname.replace("___", "_")
        outname = outname.replace("__", "_")
        args += ["-o", outname]
    args.append(url)
    w.text.insert("1.0", "Starting download...\n")
    try:
        state.process = sp.Popen(args, stdout=sp.PIPE, stderr=sp.DEVNULL, cwd=outdir)
        w.text.insert("end", "Download started...\n")
        w.run["state"] = "disabled"
        w.cancel["state"] = "enabled"
        # Submit callback to monitor the progress of the download.
        root.after(20, monitor)
    except OSError as e:
        w.text.insert("1.0", f"Error when starting download: “{e}”.")
        state.process = None


def monitor():
    """Callback to monitor the progress of the yt-dlp run."""
    if state.process is None:
        return
    rc = state.process.poll()
    if rc is None:
        # Process is still running
        text = state.process.stdout.read()
        w.text.insert("end", text)
        w.text.see("end")
        # Re-submit callback
        root.after(20, monitor)
        return
    elif rc == 0:
        # Process finished normally
        w.text.insert("end", "Download finished normally")
    else:
        w.text.insert(
            "end", f"Download process returned error code {state.process.returncode}."
        )
    w.run["state"] = "enabled"
    w.cancel["state"] = "disabled"


def do_cancel():
    state.process.terminate()
    state.process = None
    w.run["state"] = "enabled"
    w.cancel["state"] = "disabled"


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
