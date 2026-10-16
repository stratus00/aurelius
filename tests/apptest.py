# apptest.py — navigate, check off, delete
import time, lists, display
from buttons import Buttons

lists.load()
btn = Buttons()
sel = 0
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
            lists.toggle(sel); changed = True
        elif e == "ACTION_LONG" and n:
            lists.delete(sel)
            sel = max(0, min(sel, len(lists.items()) - 1))
            changed = True
        if changed:
            display.draw_list(sel)
    time.sleep_ms(10)
