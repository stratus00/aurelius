# buttons.py — turns raw presses into events
from machine import Pin
import time

PINS = {"UP": 2, "DOWN": 3, "ACTION": 4}
DEBOUNCE_MS = 30     # ignore contact chatter shorter than this
LONG_MS = 800        # hold this long for a long press or combo

class Buttons:
    def __init__(self):
        self.pins = {k: Pin(n, Pin.IN, Pin.PULL_UP) for k, n in PINS.items()}
        self.raw = {k: False for k in PINS}     # instant reading
        self.down = {k: False for k in PINS}    # debounced reading
        self.changed = {k: 0 for k in PINS}     # when raw last changed
        self.since = {k: 0 for k in PINS}       # when debounced press began
        self.group = set()   # buttons pressed since everything was last released
        self.used = False    # a hold event already fired for this group

    def poll(self):
        now = time.ticks_ms()
        released = False

        # 1. Debounce each button
        for k, p in self.pins.items():
            r = p.value() == 0
            if r != self.raw[k]:
                self.raw[k] = r
                self.changed[k] = now
            elif r != self.down[k] and time.ticks_diff(now, self.changed[k]) >= DEBOUNCE_MS:
                self.down[k] = r
                if r:
                    self.since[k] = now
                    self.group.add(k)
                else:
                    released = True

        held = [k for k in PINS if self.down[k]]

        # 2. Holds fire once, while still held
        if held and not self.used:
            held_for = min(time.ticks_diff(now, self.since[k]) for k in held)
            if held_for >= LONG_MS:
                if len(held) == 2 and "ACTION" in held:
                    self.used = True
                    other = [k for k in held if k != "ACTION"][0]
                    return other + "+ACTION"
                if held == ["ACTION"] and self.group == {"ACTION"}:
                    self.used = True
                    return "ACTION_LONG"

        # 3. Taps fire when everything is released
        if released and not held:
            group, used = self.group, self.used
            self.group = set()
            self.used = False
            if not used and len(group) == 1:
                return group.pop()
        return None
