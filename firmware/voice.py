# voice.py — push-to-talk recording into RAM (V1). upload + apply come later.
# mic gives 24-bit audio in 32-bit frames; packed to 16-bit mono PCM on the fly.
# NO flash writes while recording: they pause interrupts and stall the I2S stream.
import micropython, time
from machine import I2S, Pin

RATE = 16000        # samples/s
CHUNK = 512         # samples per read (32 ms)
SHIFT = 14          # 32-bit -> 16-bit; 16 = raw level, 14 = x4 gain (INMP441 is quiet)
MAX_S = 6           # seconds that fit in BUF

BUF = bytearray(RATE * 2 * MAX_S)    # 192 KB, allocated once at import
_raw = bytearray(CHUNK * 4)

@micropython.viper
def _pack(src, dst, off: int, n: int, shift: int):
    # 32-bit samples -> 16-bit at dst[off..], with gain + clipping
    s = ptr32(src)
    d = ptr16(dst)
    i = 0
    while i < n:
        v = s[i] >> shift
        if v > 32767:
            v = 32767
        elif v < -32768:
            v = -32768
        d[off + i] = v
        i += 1

def record(held):
    # records into BUF while held() is True. returns bytes recorded.
    mic = I2S(0, sck=Pin(16), ws=Pin(17), sd=Pin(18), mode=I2S.RX,
              bits=32, format=I2S.MONO, rate=RATE, ibuf=20000)
    n = 0
    cap = len(BUF) // 2              # capacity in samples
    try:
        for _ in range(6):           # mic needs ~85 ms to wake; skip ~200 ms
            mic.readinto(_raw)
        while held() and n + CHUNK <= cap:
            mic.readinto(_raw)
            _pack(_raw, BUF, n, CHUNK, SHIFT)
            n += CHUNK
    finally:
        mic.deinit()
    return n * 2

@micropython.viper
def peak(buf, nbytes: int) -> int:
    # loudest sample in buf[:nbytes], no copy
    d = ptr16(buf)
    p = 0
    i = 0
    n = nbytes >> 1
    while i < n:
        v = d[i]
        if v > 32767:
            v -= 65536               # ptr16 reads unsigned; make it signed
        if v < 0:
            v = 0 - v
        if v > p:
            p = v
        i += 1
    return p
