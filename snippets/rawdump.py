# rawdump.py v3 — same dump, with/without the GP18 internal pull-down (RP2350 E9)
# the one to keep: quick health check for the mic. healthy = L "low bits used" ~512/512.
from machine import I2S, Pin, mem32
import array

PAD18 = 0x40038000 + 0x04 + 18 * 4      # PADS_BANK0 GPIO18 control register
PDE, PUE = 1 << 2, 1 << 3                # pull-down / pull-up enable bits

def test(label, fix):
    mic = I2S(0, sck=Pin(16), ws=Pin(17), sd=Pin(18), mode=I2S.RX,
              bits=32, format=I2S.STEREO, rate=16000, ibuf=20000)
    if fix:
        mem32[PAD18] &= ~(PDE | PUE)     # no internal pulls on SD
    print("%s pad18=%03x" % (label, mem32[PAD18] & 0x1ff))
    buf = array.array('i', [0] * 1024)
    for _ in range(10):
        mic.readinto(buf)
    mic.readinto(buf)
    mic.deinit()
    for ch, name in ((0, "L"), (1, "R")):
        w = [buf[i] for i in range(ch, 1024, 2)]
        low = sum(1 for x in w if x & 0x00ffff00)
        print("   %s low bits used in %3d/512   e.g. %s" % (
            name, low, " ".join("%08x" % (x & 0xffffffff) for x in w[:4])))

test("A: as is      ", False)
test("B: no pulldown", True)
