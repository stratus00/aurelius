# led_pulse.py — P5 test 2. PWM "breathing" = the voice-mode look. 2 breaths / ~4 s.
# blocking version; replaced by timer-driven led.py in P8.
from machine import Pin, PWM; import time, math
led = PWM(Pin(15)); led.freq(1000)
for i in range(400):
    led.duty_u16(int((1 - math.cos(i / 100 * math.pi)) / 2 * 65535))
    time.sleep_ms(10)
led.duty_u16(0)
