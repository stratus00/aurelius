# rawdump.py v1 — raw I2S words from the mic, quiet room. shows if bits are aligned.
from machine import I2S, Pin
import array

mic = I2S(0, sck=Pin(16), ws=Pin(17), sd=Pin(18), mode=I2S.RX,
          bits=32, format=I2S.MONO, rate=16000, ibuf=20000)
buf = array.array('i', [0] * 512)
for _ in range(10):                 # skip ~320 ms of startup
    mic.readinto(buf)
mic.readinto(buf)                   # stay quiet for this one
mic.deinit()

print("first 12 raw words (hex, top-16-bit value):")
for x in buf[:12]:
    print("%08x %d" % (x & 0xffffffff, x >> 16))
low = sum(1 for x in buf if x & 0xff)
s = [x >> 16 for x in buf]
print("low byte nonzero in %d/512 words (expect ~0)" % low)
print("quiet: mean %d, min %d, max %d" % (sum(s) // len(s), min(s), max(s)))
