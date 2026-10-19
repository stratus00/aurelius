# led.py — the LED's vocabulary, run by a background timer
from machine import Pin, PWM, Timer
import math

TICK_MS = 20
ON = 65535

_pwm = PWM(Pin(15))
_pwm.freq(1000)
_pwm.duty_u16(0)

# A pattern is a tuple of (brightness, ticks) steps; 1 tick = 20 ms
BLINK   = ((ON, 6), (0, 1))                               # one ~120 ms flash
DOUBLE  = ((ON, 5), (0, 5), (ON, 5), (0, 1))              # two quick flashes
FLICKER = ((ON, 2), (0, 2)) * 6 + ((0, 1),)               # fast, urgent
PULSE   = tuple((int((1 - math.cos(i * math.pi / 50)) / 2 * ON), 1)
                for i in range(100))                      # one 2 s breath

_pat = None
_i = 0
_left = 0
_loop = False

def _tick(t):
    # Runs every 20 ms in the background. No new objects are created here.
    global _pat, _i, _left
    if _pat is None:
        return
    if _left > 0:
        _left -= 1
        return
    if _i >= len(_pat):
        if _loop:
            _i = 0
        else:
            _pat = None
            _pwm.duty_u16(0)
            return
    d, n = _pat[_i]
    _pwm.duty_u16(d)
    _left = n - 1
    _i += 1

_timer = Timer(period=TICK_MS, mode=Timer.PERIODIC, callback=_tick)

def _play(p, loop=False):
    global _pat, _i, _left, _loop
    _pat = None
    _i = 0
    _left = 0
    _loop = loop
    _pat = p

def blink():   _play(BLINK)
def double():  _play(DOUBLE)
def flicker(): _play(FLICKER)
def pulse():   _play(PULSE, loop=True)    # keeps going until off()

def off():
    global _pat
    _pat = None
    _pwm.duty_u16(0)
