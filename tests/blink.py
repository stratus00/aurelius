# blink.py — P1. First file saved TO the Pico. Onboard LED x10.
# Onboard LED on Pico W goes through the Wi-Fi chip -> Pin("LED"), not a number.
from machine import Pin
import time

led = Pin("LED", Pin.OUT)
for i in range(10):
    led.toggle()
    time.sleep(0.25)
print("Aurelius: Pico alive")
