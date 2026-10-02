# led_blink.py — P5 test 1. Blue LED on GP15 (220 ohm), blink x3.
from machine import Pin; import time
led = Pin(15, Pin.OUT)
for _ in range(3):
    led.on(); time.sleep(0.3); led.off(); time.sleep(0.3)
