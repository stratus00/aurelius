# vtest.py — V2. hold UP+ACTION, speak, release -> clip uploads to the relay.
from machine import Pin
import gc, time
import voice, led, net, lists

up = Pin(2, Pin.IN, Pin.PULL_UP)
act = Pin(4, Pin.IN, Pin.PULL_UP)
held = lambda: up.value() == 0 or act.value() == 0

lists.load()
print("1. wifi...")
net.wifi()
gc.collect()
print("   ok, free RAM:", gc.mem_free())

print("2. Hold UP+ACTION...")
while not (up.value() == 0 and act.value() == 0):
    time.sleep_ms(10)
time.sleep_ms(800)
led.pulse()
print("3. speak now, release when done")
nbytes = voice.record(held)
led.off()
print("4. recorded %.2f s, uploading..." % (nbytes / 32000))

t0 = time.ticks_ms()
res = net.post_voice(lists.data, memoryview(voice.BUF)[:nbytes])
print("5. reply in %d ms:" % time.ticks_diff(time.ticks_ms(), t0), res)
