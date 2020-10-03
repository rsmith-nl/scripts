#!/usr/bin/env python3
# file: gtk-razer.pyw
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2020 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2020-03-26T20:44:32+0100
# Last modified: 2020-05-15T06:48:00+0200
"""Set the LEDs on a Razer keyboard to a static RGB color.

Uses the GTK+ GUI toolkit.

Tested on an Ornata Chroma and a BlackWidow Elite.
The USB control transfer messages were compiled by tracing what the
Openrazer (https://github.com/openrazer/openrazer) driver code does.
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

__version__ = "2020.05.15"


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
        "on_quit": on_quit
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


def on_quit(arg=None):
    R = int(widgets.red.get_value())
    G = int(widgets.green.get_value())
    B = int(widgets.blue.get_value())
    write_rc(state.rcpath, R, G, B)
    Gtk.main_quit()


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
    state.rcpath = '.' + os.path.splitext(os.path.basename(sys.argv[0]))[0] + 'rc'
    state.model = "No Razer keyboard found!"
    # Find devices
    devs = list(usb.core.find(find_all=True, idVendor=0x1532))
    if devs:
        state.dev = devs[0]
        state.model = devs[0].product
    return state


def read_rc(rcpath):
    """Retrieve color values from the rc file.

    Arguments:
        rcpath (str): path to the rc file.

    Returns:
        3-tuple of integers representing R,G,B.
    """
    if not os.path.exists(rcpath):
        return None
    with open(rcpath) as rc:
        colors = [int(ln) for ln in rc.readlines() if ln.strip()[0] in '1234567890']
    if len(colors) != 3:
        return None
    return colors


def write_rc(rcpath, R, G, B):
    with open(rcpath, 'w') as rc:
        rc.write(f'{R}\n')
        rc.write(f'{G}\n')
        rc.write(f'{B}\n')


# The definition of the user interface was made with Glade.
# It was encapsulated by the py-include script as follows:
#    python3 py-include.py -c -t gtk-razer.glade
ui = zlib.decompress(base64.b85decode(
    'c-rlnO>f&c5Qgvl6<l5mf2IL;0oz5|BDw6L=m+*FP~uo(O_N%Zvg3c>k>u1?Oj(v4rw*E1V$Dl'
    '&W*&}*lZ@Wq&m~!au|lgc9d!GYfQmF1Djw7C-)=j9)Ay4%qrW;Gat8_wbHK?`xP-)#aUfUS;jl'
    'X(oemla<-kl?1d}&}j12sr2?Lf$5sqo>W^d`{MJVgjUSX%h9}qbbNoMVs-nrQg|B+cY2jwUcd`'
    '#H~nE}mh(K<Cc1>;sku{n%smf~-8GQ7SX^&TGiEv<tz5GpcItUMVs2~rkAMbNJ*M!j<92Rd<Q0'
    'Mv{3;tTMX=EHwNalI_}Z?twb`;V9kraH<jo!l~MVP{iT#EQwa^$b=W0}_~p4lIiJBusG$W=ypT'
    '@G&KJ$uK7PR;5eSagityl9xZ{Tab8I5-mBH2ZP?0#Utw-&+d$P$cE3Og|H%&cyhj(Y{#8rLg3R'
    'Fy$o#1BCHp5a&^#Kw9MveBf9pADz5w8|ByMSRhigu17_WOB@01P;tW$(GRH79W4Z!#7PY=T92L'
    '`sxVDiQh(IjB1{|g=ldhfGX)T>d0|)oc>-9$jHU{DnAgO_cfF;4yXhWPP26(sjMU{gPNfFI3_7'
    '(h1{(%So^#WVRb+daG%@Bu%6vEU6%sCb%bkaXO66r6|z%Rm2AHTnH5|2W1yW+QpvQWQbS-~>SV'
    '{!_Z#R3<K=I|NO-0G;>lbMTO!K{E8Vn|NmGS^=ymRHY*CEgd@(Nunv+WwJP=6<iK)UjdnQ#dR#'
    'aG4ywJ1>V{BZfQ_7~1Auaw)h=g8YUH)_E^Imp~rd+}<XvMUy)fQU(&QHL{g!MrVo#T*SiJ7D;X'
    'vRJkq6aA(1alDQ49l>#qPL1}P)iU$|ie{NHJNc;H$Id0V#zmj}5l84Vn@&VoI3k11M8~w`h**H'
    'FPe|w7^SrfdcB3L`DtL>nJdnPf3`%=8)o8P~ie4Uc$N47`$d5W*Kgrtn~V%Rts?$vso_B;N`uq'
    '7^eV}Py8RHB#Er){iOgX{jjUHMi>K*WhVX^Dfg;ho`wvcloD=75Zxno*yA&P*&+VDc!S_k$z#S'
    'O{vr$r{C>#;fa`PX1}sSIQ+vaH?gp{G_%z?yHhDm1&>AYh02~+$#Nb$!<RT|9b5%<=od!3O<+9'
    'oBG8Lj@uJ`Zw;UDCQ(-^o^_C8;rKbuS8#ve6bHR7W;iogg_;>oLQIOx6Sp2RGE4F=7)6BI9zh;'
    'G?7<WT#meVz%Z3*??kP)G0c&3KE~!ClWaSe$bO!hamfVGIs|L`!aPg!r?!T`??>{LDyMJ@P5M?'
    '#QTMsu6M!l_nvH1yWMXp`'
)).decode("utf-8")


if __name__ == '__main__':
    # Detach from the command line on UNIX systems.
    if os.name == 'posix':
        if os.fork():
            sys.exit()
    # Create the GUI and run it.
    state = create_state()
    colors = read_rc(state.rcpath)
    root, widgets = create_widgets()
    if colors:
        widgets.red.set_value(colors[0])
        widgets.green.set_value(colors[1])
        widgets.blue.set_value(colors[2])
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
