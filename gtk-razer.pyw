#!/usr/bin/env python3
# file: gtk-razer.pyw
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2020 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2020-03-26T20:44:32+0100
# Last modified: 2020-03-26T22:17:48+0100
"""Set the LEDs on a Razer keyboard to a static RGB color.

Uses the GTK+ GUI toolkit.

Tested on an Ornata Chroma and a BlackWidow Elite.
The USB control transfer messages were laboriously extracted from the
Openrazer (https://github.com/openrazer/openrazer) driver code.
"""

from types import SimpleNamespace
from functools import partial
import base64
import os
import sys
import zlib
import usb.core

import gi
gi.require_version('Gtk', '3.0')  # noqa
from gi.repository import Gtk, Gdk

__version__ = '0.1'


def create_widgets():
    # Namespace to save widgets that we need to reference later.
    w = SimpleNamespace()
    # Load the UI definition.
    builder = Gtk.Builder()
    builder.add_from_string(ui)
    # Root window
    root = builder.get_object("root")
    # Type label
    tp = builder.get_object("type")
    tp.props.label = state.model
    # Red
    bRed = builder.get_object("bRed")
    bRed.connect("clicked", partial(set_preview, red=255))
    sRed = builder.get_object("sRed")
    sRed.connect("change-value", on_slider_change)
    w.red = sRed
    # Green
    bGreen = builder.get_object("bGreen")
    bGreen.connect("clicked", partial(set_preview, green=255))
    sGreen = builder.get_object("sGreen")
    sGreen.connect("change-value", on_slider_change)
    w.green = sGreen
    # Blue
    bBlue = builder.get_object("bBlue")
    bBlue.connect("clicked", partial(set_preview, blue=255))
    sBlue = builder.get_object("sBlue")
    sBlue.connect("change-value", on_slider_change)
    w.blue = sBlue
    # Preview
    da = builder.get_object("show")
    da.connect('draw', on_draw)
    w.show = da
    quit = builder.get_object("quit")
    quit.connect("clicked", Gtk.main_quit)
    # Set button
    s = builder.get_object("set")
    s.connect("clicked", set_color)
    return root, w


def set_preview(w, red=0, green=0, blue=0):
    """Callback for sliders."""
    widgets.red.set_value(red)
    widgets.green.set_value(green)
    widgets.blue.set_value(blue)
    widgets.show.queue_draw()


def on_key(w, event):
    """Callback for keypresses."""
    key = Gdk.keyval_name(event.keyval)
    if key in ['q', 'Q']:
        Gtk.main_quit()


def on_draw(da, ctx):
    """Fill the drawingarea with a color."""
    w, h = da.get_allocated_width(), da.get_allocated_height()
    ctx.rectangle(0, 0, w, h)
    ctx.set_source_rgb(
        widgets.red.get_value()/255,
        widgets.green.get_value()/255,
        widgets.blue.get_value()/255,
    )
    ctx.fill()
    return True


def on_slider_change(rng, scroll, value):
    """Change the slider value"""
    widgets.show.queue_draw()


def static_color_msg(red, green, blue):
    """
    Create a message to set the Razer Ornata Chroma lights to a static color.
    All arguments should be an number in the range 0-255.

    Returns an bytes object containing the message ready to feed into a ctrl_transfer.
    """
    # Meaning of the bytes, in sequence: 0x00 = status, 0x3f = transaction id,
    # 0x00,0x00 = number of remaining packets, 0x00 = protocol type,
    # 0x09 = length of used arguments, 0x0f = command class, 0x02 = command id.
    hdr = b'\x00\x3f\x00\x00\x00\x09\x0f\x02'
    # Meaning of the nonzero bytes, in sequence: 0x01 = VARSTORE,
    # 0x05 = BACKLIGHT_LED, 0x01 = effect id, 0x01 = unknown
    arguments = b'\x01\x05\x01\x00\x00\x01'
    msg = hdr + arguments + bytes([red, green, blue])
    chksum = 0
    for j in msg[2:]:  # Calculate the checksum
        chksum ^= j
    msg += bytes(88 - len(msg))  # Add filler; the total message buffer is 90 bytes.
    msg += bytes([chksum, 0])  # Add checksum and zero byte, completing the msg.
    return msg


def set_color(w):
    """Callback to set the color."""
    msg = static_color_msg(
        int(widgets.red.get_value()),
        int(widgets.green.get_value()),
        int(widgets.blue.get_value())
    )
    # 0x21: request_type USB_TYPE_CLASS | USB_RECIP_INTERFACE | USB_DIR_OUT
    # 0x09: request HID_REQ_SET_REPORT
    # 0x300: value
    # 0x01: report index HID_REQ_GET_REPORT
    state.dev.ctrl_transfer(0x21, 0x09, 0x300, 0x01, msg)


def create_state():
    """Create the global state."""
    state = SimpleNamespace()
    state.dev = None
    state.model = "No Razer keyboard found!"
    # Find devices
    devs = list(usb.core.find(find_all=True, idVendor=0x1532))
    if devs:
        state.dev = devs[0]
        state.model = devs[0].product
    return state


# The definition of the user interface was made with Glade.
# It was encapsulated by the to_include script.
ui = zlib.decompress(base64.b85decode(
    'c-rk+O>f&c5WV+Tu)Hq(nFeS9TSdBUa_M1r)5RVIN*qh9X;LLAJO1}OlA79%Da&#aLuq?U!g(a'
    '$%p?6c&gA{wLXssIE3}%@QGZAYs91BMk}3W7%XRN9eILA<yzceL4Ja_o0VgZrQj$o<fn4;*<Nk'
    '>BdKe^>12bbW1g{9082FY81C~e;O=;rhf6&cB2piHt8K<MK5IYh}X6=;TxcL?Tnp?L3<tPz+O4'
    '$dQ11(}PIx{*0<JLs61x#t4;cqk;UtUfI_e1_j>mUn-iVc)A2csrH#uC^840jQeLACQEN!%C!_'
    '2OCl1N^0N_)jRVSJnQF)~;s%F;n48$GN4!HIo+hHf2SknEW0+hjq_@1ZJTJ%Q8PHQ(S_XQmsN9'
    'ro^ro<^)$&x{^9h5~o7)>gQq$5)VtNB?ogKFxZNC5WUCj#)$iB_!upP6_Lb~^Tp(QbWTZu4`cK'
    'yv>A)>zM#RyQLAW~FVqHf=>_dj_tXE7JEv7u*k~inx^*RsKvLoiQ&uv^Ff~)U1|*AE-yTlNX+v'
    'JyzzoD7mS95;GnPx&4(+s-PGq5jJLhHnCki$J;!+@)fu(>I!P00$oF)c%-@nlIS=%hl;yKo`A^'
    '$LQA#;w!DGi3l)5v~+Ms-`-TYu*mousGj>$<(7O7w3{3D`&~DN@owQH{?isx2eaUQ-45x1@His'
    'R&cjK}lVlPf}>H-N}mj8^OPzqCVXTS3Y5Mj%h9Ag*7P!Rtl?wf_n43g1U_vR<_iWZT3+s!Ce{_'
    'uRE~LYxujMA+~wB1gwR@n+YjHiI!frqGoiic*sQ}oIPMvo<u^U4tl3;2_0jdUZ99tdAgrfM&t9'
    'z=m@j)0#($;#r>=zdS-ugZE!{Uy!Ef`kJLJ_@Qz85s6!55kDH(0RWVN`rw6eo@_Y=}T7_hc^Rm'
    'A)8Xv@ZN&AU^G;D=aUKwED?}${ds1MtCRg5l&hj!(gAqA17?om@5T@7#B6qFSXeen?$d2B^}_y'
    'sd)ltWWw0ojjE#N$O!`!Ui8jx;`f7BqO*h~Mefaum*PgSPsMr$hT-8qY0Rb2A+Rc!MkD6SvNOJ'
    'kpxa{%3DoSI&LyOY^Vl<z7G8(Rq8K&#mzjdg!{V;;fAT3#a!1ZsAvK10d`2(LaZEq?zF)!lKBc'
    'aOda)j62u|s4kaMPQ|U%B@5M9&5z)a4Dd}k3kv;K7R@_xInq53J$zCr?0*s25#(-)w+1%@lfl;'
    'i9sCav!N=+'
)).decode("utf-8")


if __name__ == '__main__':
    # Detach from the command line on UNIX systems.
    if os.name == 'posix':
        if os.fork():
            sys.exit()
    # Create the GUI and run it.
    state = create_state()
    root, widgets = create_widgets()
    root.connect("destroy", Gtk.main_quit)
    root.connect("key-press-event", on_key)
    root.set_modal(True)  # Makes a floating window.
    root.show_all()
    Gtk.main()
