# apptest.py — the full non-voice app: lists, picker, LED
import time, lists, display, led
from buttons import Buttons

lists.load()
btn = Buttons()
mode = "list"     # "list" or "picker"
sel = 0           # selected item in list view
psel = 0          # selected list in picker
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
    elif e == "UP+ACTION":                  # voice-mode preview
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
        return                              # nothing changed
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
    elif e == "ACTION":                     # open the selected list
        lists.switch(names[psel])
        led.blink()
        mode, sel = "list", 0
        display.draw_list(sel)
    elif e == "DOWN+ACTION":                # cancel
        mode = "list"
        display.draw_list(sel)

display.draw_list(sel, full=True)
print("Ready. Press Stop to quit.")
while True:
    e = btn.poll()
    if e:
        print(mode, e)
        if mode == "list":
            list_view(e)
        else:
            picker(e)
    time.sleep_ms(10)
