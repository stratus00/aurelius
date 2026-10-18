# rectest.py v4 — V1. record to RAM, then save rec.pcm AFTER recording stops.
from machine import Pin
import gc, time
gc.collect(); print("free RAM before:", gc.mem_free())
import voice, led
print("free RAM after 192 KB buffer:", gc.mem_free())

up = Pin(2, Pin.IN, Pin.PULL_UP)
act = Pin(4, Pin.IN, Pin.PULL_UP)
held = lambda: up.value() == 0 or act.value() == 0

print("1. Hold UP+ACTION together...")
while not (up.value() == 0 and act.value() == 0):
    time.sleep_ms(10)
print("2. both pressed, keep holding")
time.sleep_ms(800)
led.pulse()
print("3. LED pulsing: speak now, release when done (max 6 s)")
t0 = time.ticks_ms()
nbytes = voice.record(held)
wall = time.ticks_diff(time.ticks_ms(), t0) / 1000
led.off()
print("4. released")

with open("rec.pcm", "wb") as f:              # safe now: mic is off
    f.write(memoryview(voice.BUF)[:nbytes])
print("recorded %.2f s of audio in %.2f s wall time" % (nbytes / 32000, wall))
print("saved rec.pcm, %d bytes" % nbytes)
print("peak %d (of 32767)" % voice.peak(voice.BUF, nbytes))
