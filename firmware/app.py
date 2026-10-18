# app.py — Aurelius: list view, list picker, LED feedback
import time, lists, display, led
from buttons import Buttons

IDLE_MS = 60000     # put the display to sleep after 1 min without a press

mode = "list"       # "list" or "picker"
sel = 0             # selected item in list view
psel = 0            # selected list in picker
pulsing = False

def list_view(e):
    global sel, psel, mode, pulsing
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
    elif e == "UP+ACTION":                  # voice-mode preview (for now)
        pulsing = not pulsing
        if pulsing: led.pulse()
        else: led.off()
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

def run():
    lists.load()
    btn = Buttons()
    display.draw_list(sel, full=True)
    print("Aurelius running. Press Stop to quit.")
    last = time.ticks_ms()
    while True:
        e = btn.poll()
        if e:
            last = time.ticks_ms()
            if mode == "list":
                list_view(e)
            else:
                picker(e)
        elif time.ticks_diff(time.ticks_ms(), last) > IDLE_MS:
            display.sleep()                 # does nothing if already asleep
        time.sleep_ms(10)
