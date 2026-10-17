# ledtest.py — shows each pattern once
import time, led
print("blink");   led.blink();   time.sleep(1)
print("double");  led.double();  time.sleep(1)
print("flicker"); led.flicker(); time.sleep(1)
print("pulse");   led.pulse();   time.sleep(4)
led.off(); print("done")
