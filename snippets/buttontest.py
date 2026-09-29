# buttontest.py — P4. Raw button read, prints only on change. Stop to quit.
# pull-up: released = 1, pressed = 0
from machine import Pin
import time
b = {"UP": Pin(2, Pin.IN, Pin.PULL_UP),
     "DOWN": Pin(3, Pin.IN, Pin.PULL_UP),
     "ACTION": Pin(4, Pin.IN, Pin.PULL_UP)}
last = {k: 1 for k in b}
while True:
    for k, p in b.items():
        v = p.value()
        if v != last[k]:
            print(k, "pressed" if v == 0 else "released")
            last[k] = v
    time.sleep_ms(20)
