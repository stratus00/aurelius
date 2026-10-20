# app.py — Aurelius: list view, list picker, LED feedback, sleep screen, voice
import time, lists, display, led, net, voicecmd
from machine import Pin
from buttons import Buttons

IDLE_MS = 60000     # show the sleep screen after 1 min without a press

mode = "list"       # "list" or "picker"
sel = 0             # selected item in list view
psel = 0            # selected list in picker
asleep = False
_pins = [Pin(2), Pin(3), Pin(4)]    # UP, DOWN, ACTION (read-only here)

def list_view(e):
    global sel, psel, mode
    n = len(lists.items())
    if e == "UP" and sel > 0:
        sel -= 1
    elif e == "DOWN" and sel < n - 1:
        sel += 1
    elif e == "ACTION" and n:
        lists.toggle(sel)
        if lists.items()[sel]["done"]:
            led.blink()
    elif e == "ACTION_LONG" and n:
        led.double()
        lists.delete(sel)
        sel = max(0, min(sel, len(lists.items()) - 1))
    elif e == "UP+ACTION":                  # voice: hold, speak, release
        before = lists.current_name()
        say = voicecmd.run()
        if lists.current_name() != before:
            sel = 0
        sel = max(0, min(sel, len(lists.items()) - 1))
        display.draw_list(sel)
        display.toast(say)
        return
    elif e == "DOWN+ACTION":                # open the picker
        mode = "picker"
        psel = lists.names().index(lists.current_name())
        display.draw_picker(psel)
        return
    else:
        return
    display.draw_list(sel)

def picker(e):
    global sel, psel, mode
    names = lists.names()
    if e == "UP" and psel > 0:
        psel -= 1
        display.draw_picker(psel)
    elif e == "DOWN" and psel < len(names) - 1:
        psel += 1
        display.draw_picker(psel)
    elif e == "ACTION":
        lists.switch(names[psel])
        led.blink()
        mode, sel = "list", 0
        display.draw_list(sel)
    elif e == "DOWN+ACTION":                # cancel
        mode = "list"
        display.draw_list(sel)

def wake():
    # first press after the sleep screen only brings the screen back
    global asleep
    asleep = False
    if mode == "list":
        display.draw_list(sel)
    else:
        display.draw_picker(psel)

def _settle(btn):
    # after a voice command: wait for all buttons up, then discard anything
    # the button handler queued during the long hold (no stray check/delete)
    while any(p.value() == 0 for p in _pins):
        time.sleep_ms(10)
    t0 = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), t0) < 200:
        btn.poll()
        time.sleep_ms(10)

def run():
    global asleep
    lists.load()
    try:
        net.start()                         # join wifi in the background
    except Exception as ex:
        print("wifi start failed:", ex)
    btn = Buttons()
    display.draw_list(sel, full=True)
    print("Aurelius running. Press Stop to quit.")
    last = time.ticks_ms()
    while True:
        e = btn.poll()
        if e:
            if asleep:
                wake()
            elif mode == "list":
                list_view(e)
                if e == "UP+ACTION":
                    _settle(btn)
            else:
                picker(e)
            last = time.ticks_ms()
        elif not asleep and time.ticks_diff(time.ticks_ms(), last) > IDLE_MS:
            display.saver()
            asleep = True
        time.sleep_ms(10)
