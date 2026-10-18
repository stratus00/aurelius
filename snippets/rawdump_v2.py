# rawdump.py v2 — which rate / channel gives full 24-bit data?
from machine import I2S, Pin
import array

def test(rate):
    mic = I2S(0, sck=Pin(16), ws=Pin(17), sd=Pin(18), mode=I2S.RX,
              bits=32, format=I2S.STEREO, rate=rate, ibuf=20000)
    buf = array.array('i', [0] * 1024)
    for _ in range(10):
        mic.readinto(buf)
    mic.readinto(buf)
    mic.deinit()
    for ch, name in ((0, "L"), (1, "R")):
        w = [buf[i] for i in range(ch, 1024, 2)]
        low = sum(1 for x in w if x & 0x00ffff00)
        print("%5d %s  low bits used in %3d/512   e.g. %s" % (
            rate, name, low, " ".join("%08x" % (x & 0xffffffff) for x in w[:4])))

for r in (16000, 32000, 48000):
    test(r)
