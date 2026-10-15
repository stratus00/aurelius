# navtest.py — UP/DOWN move the highlight; every event prints
# check: DOWN scrolls past row 7 | UP at top = no move | DOWN at bottom = no move
# ACTION tap -> ACTION | hold ACTION ~1s -> ACTION_LONG once | UP+ACTION / DOWN+ACTION hold -> combo once
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
        if e == "UP" and sel > 0:
            sel -= 1
            display.draw_list(sel)
        elif e == "DOWN" and sel < n - 1:
            sel += 1
            display.draw_list(sel)
    time.sleep_ms(10)
