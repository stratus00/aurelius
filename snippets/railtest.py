# railtest.py — P2. No-multimeter rail check. Ran in Shell (one line each).
# test jumper a1 (GP0) -> LEFT + rail, replug:
from machine import Pin; Pin(0, Pin.IN, Pin.PULL_DOWN).value()   # expect 1
# move jumper a1 -> LEFT - rail, replug:
from machine import Pin; Pin(0, Pin.IN, Pin.PULL_UP).value()     # expect 0
# result: 1 then 0 = both rails live. remove test jumper after.
