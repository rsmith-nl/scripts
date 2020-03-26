#!/usr/bin/env python3
# file: gtk-razer.pyw
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2020 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2020-03-26T20:44:32+0100
# Last modified: 2020-03-26T23:55:33+0100
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
    handlers = {
        "on_key": on_key,
        "on_red": partial(set_preview, red=255),
        "on_green": partial(set_preview, green=255),
        "on_blue": partial(set_preview, blue=255),
        "on_slider_change": on_slider_change,
        "on_draw": on_draw,
        "set_color": set_color,
        "on_quit": Gtk.main_quit
    }
    builder.connect_signals(handlers)
    # Root window
    root = builder.get_object("root")
    # Type label
    tp = builder.get_object("type")
    tp.props.label = state.model
    # Red
    sRed = builder.get_object("sRed")
    w.red = sRed
    # Green
    sGreen = builder.get_object("sGreen")
    w.green = sGreen
    # Blue
    sBlue = builder.get_object("sBlue")
    w.blue = sBlue
    # Preview
    da = builder.get_object("show")
    # da.connect('draw', on_draw)
    w.show = da
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
    'c-rlnUvt|w48Y&}DLB6F{5Q+pc4w=Xu1j9_u&v$oQAdfe#hNBHlCtA(KS)YyE2b>Vj#K5Dw?qO'
    '+0{9UEkWAj+FC|%lu|lgU9rcHlfQmI2YCfg^e!lJfO5X?XCO`Fh<PH=V=75v6a0!`9#(`Y*$K('
    'Ep^m-^HlmjzkF$C`jnHcyl69z1iBAU{<Tl`G78==~e4hlIPeTCSOSTbv;^v*4A_}9$3B`8OU;8'
    'V&z$P8#Mi_)plDHyjQiY;MEvlM@$!T9=mGI)IDm$VMjP^j2Iv2rkKQb^exDhk7@#$-^Q{75724'
    '1jv|R{R6}wb}4RD6ZG#`Hj}D=KL{J;Y`PwrNJ$e7WNKh#auD@AiaQ1&wvDGp$DtNKM7M@f|*jS'
    'LVQh$T{H9v?y7W&IxZ3?Lh|zG{0I^+OQIzQ^C&Rbk$57#XW5+*kJ0d1v=UZC5^v6DlkJ&viVJ)'
    '?Mz2GgvKaFP4X%#bMayidwo2DtrHbi(^FL(HX;lU`+JafPuVfKON}OTJO6C~4W=c1J#-gt83@7'
    '=t!LM!948$N-U_%ZwmPyx6+i5MGNJ9tr&TIAW2<#k)OMs*XRsz-pL!%9Gni$~y+Knm~A(kRupz'
    'kaAoBV+X|Az&3uIu*nEM6cE4IzY?3z>5)PG~SZ-V^CJrIB9=pFZ8cauZKNayR3*hqBOq!&1PO%'
    '6aaRbGR%P=qQ=v7bJ71plT0huKdPjC0$17l5@Ds^*f5?)yrXt?Sea*%D++h2c+_kd*O<9OlRoU'
    '98ru(0cio}IZzhi=q8lETo%etF+(~ECT(+Fxfa|dVczY6b>0T33mmd-Cl|051@BBq8A@z%WGmB'
    '*&J+*1m<wlH1i4wE%59O8dn;Dt&s}(}6xdXSrNHGW9(Ax5-KF@LQuGya+^R-?Bl%(^k6(`DBTC'
    'm-2y&a6`i<j@aeU!o_txN!^s)%n4(@8p>F}OO4B?>=@7d<J?<QZTB>IW$iFTf2Yb_xu<GdI=j>'
    'ZRdy+->D|7h46m%K5+9@12z*VL!mn5{<F!$YU?t&o72C+@5zj*f<Ro)5|jhfU5A5ji)aKK&&#*'
    '!6@a_X1i!I#C}JLG72UQ907s$1Z8`Tcds@U2+7cnkLI9wb}7dmaNH4hZMZRCHcf{(r+Di^WFc`'
    'E7z5KUpqGVs~qLjFLt!wp6R<ae#TCsE>*nfRL8>UL!D3XBhGZt>SBVkfK8;C;UvPK$UJZl6Gvu'
    'A{((_MsNH$w$-^EDQCO^e`Lb->!EsNSx(ZnHoY$oSt&x?F;LsT0TUc@v`mG8;@505KI=_Fv3Vr'
    'yjDD40Jy(5}c7w^2>zL*Sl{@vz(!y>Zs'
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
    root.set_modal(True)  # Makes a floating window.
    if state.dev is None:
        msg = Gtk.MessageDialog(
            parent=root, message_type=Gtk.MessageType.ERROR,
            title="Warning", text="No Razer keyboard detected!",
            buttons=Gtk.ButtonsType.CLOSE
        )
        msg.run()
    else:
        root.show_all()
        Gtk.main()
