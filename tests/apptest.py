# apptest.py — navigate, check off, delete, with LED feedback
import time, lists, display, led
from buttons import Buttons

lists.load()
btn = Buttons()
sel = 0
pulsing = False
display.draw_list(sel, full=True)
print("Ready. Press Stop to quit.")

while True:
    e = btn.poll()
    if e:
        print(e)
        n = len(lists.items())
        changed = False
        if e == "UP" and sel > 0:
            sel -= 1; changed = True
        elif e == "DOWN" and sel < n - 1:
            sel += 1; changed = True
        elif e == "ACTION" and n:
            lists.toggle(sel)
            if lists.items()[sel]["done"]:
                led.blink()              # blink only when checking off
            changed = True
        elif e == "ACTION_LONG" and n:
            led.double()
            lists.delete(sel)
            sel = max(0, min(sel, len(lists.items()) - 1))
            changed = True
        elif e == "UP+ACTION":           # voice-mode preview
            pulsing = not pulsing
            led.pulse() if pulsing else led.off()
        if changed:
            display.draw_list(sel)
    time.sleep_ms(10)
