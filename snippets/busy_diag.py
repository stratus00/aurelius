# busy_diag.py — P3. Why is BUSY (GP13) reading 1? Ran in Shell.
#
# step 1 (quick check):
#   from machine import Pin; Pin(13, Pin.IN, Pin.PULL_UP).value()
#   0 = display powered + idle. 1 = run the full diag below.
#
# read table:
#   pull-down | pull-up | after reset | meaning
#   0         | 1       | 1           | nothing driving BUSY -> no power / BUSY wire not on GP13
#   any       | any     | 0           | display alive, just needed a reset -> run demo
#   1         | 1       | 1           | something holding BUSY high (rare)
#
# result: 1 1 0 -> display powered, stuck busy from power-up, reset pulse -> idle.
from machine import Pin; import time
rst = Pin(12, Pin.OUT, value=1)
print("pull-down:", Pin(13, Pin.IN, Pin.PULL_DOWN).value())
print("pull-up:  ", Pin(13, Pin.IN, Pin.PULL_UP).value())
rst.value(0); time.sleep_ms(20); rst.value(1); time.sleep_ms(200)
print("after reset:", Pin(13, Pin.IN, Pin.PULL_UP).value())
