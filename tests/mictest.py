# mictest.py — P6. INMP441 live sound meter, 10 s. quiet -> talk -> clap.
# STATUS: UNTESTED. mic header pins not soldered yet (blocked 10/07, iron ordered).
# all 0 = L/R not grounded / SD wrong hole / no VDD. huge + flat = SCK/WS swapped.
# error about ws = WS must be SCK+1 (GP17).
from machine import I2S, Pin
import array, time

mic = I2S(0, sck=Pin(16), ws=Pin(17), sd=Pin(18), mode=I2S.RX,
          bits=32, format=I2S.MONO, rate=16000, ibuf=20000)
samples = array.array('i', [0] * 512)
mic.readinto(samples)                      # throw away startup data

t0 = time.ticks_ms(); n = 0
while time.ticks_diff(time.ticks_ms(), t0) < 10000:
    mic.readinto(samples)
    n += 1
    if n % 5 == 0:
        peak = max(abs(x >> 16) for x in samples)
        print("#" * min(peak // 200, 60), peak)
mic.deinit()
