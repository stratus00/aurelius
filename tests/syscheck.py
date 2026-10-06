# syscheck.py — one-click check of everything built (P1-P5). Run at start of a session.
from machine import Pin, PWM
import time, os

print("Files on Pico:", os.listdir())

# 1. Onboard LED + external LED
Pin("LED", Pin.OUT).on()
led = PWM(Pin(15)); led.freq(1000)
for i in range(0, 65535, 1024):
    led.duty_u16(i); time.sleep_ms(15)
led.duty_u16(0)
print("LEDs: OK if both lit up")

# 2. Buttons (5 seconds - press each one)
b = {"UP": Pin(2, Pin.IN, Pin.PULL_UP),
     "DOWN": Pin(3, Pin.IN, Pin.PULL_UP),
     "ACTION": Pin(4, Pin.IN, Pin.PULL_UP)}
print("Press each button now...")
seen = set(); t0 = time.ticks_ms()
while time.ticks_diff(time.ticks_ms(), t0) < 5000:
    for k, p in b.items():
        if p.value() == 0 and k not in seen:
            print(k, "works"); seen.add(k)
print("Buttons missing:", [k for k in b if k not in seen] or "none")

# 3. Display
from epd_2in9 import EPD_2in9_Landscape
epd = EPD_2in9_Landscape()
epd.Clear(0xff); epd.fill(0xff)
epd.text("AURELIUS", 10, 10, 0x00)
epd.text("system check OK", 10, 30, 0x00)
epd.display(epd.buffer); epd.sleep()
print("Display: OK if text appeared")
