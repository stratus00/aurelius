# devlog

shorthand. newest at bottom. did / broke / fix / next.

## 2026-09-02
- did: repo + notes started. Aurelius = UU002, physical to-do list. Pico 2 W + 2.9" e-ink + 3 buttons + LED + INMP441.

## 2026-09-03
- did: lab overview (Unum Usum, lineup UU001-003) + v0 parts list.
- did: MicroPython flashed on the Pico 2 W.

## 2026-09-06
- did: v0 breadboard layout. Pico c1-h20, USB up, pin 1 top-left. GP2=row4, GP3=row5, GP4=row6, GP15=row20.
- broke: buttons — reads wrong / stuck. long debug session.
- fix: buttons have to bridge the center gap (e<->f). signal on e side, GND on f side -> right blue rail, Pico GND on same rail. all 3 work.
- lesson: generic 'plug it in near X' advice kept failing. exact row/col coords only.

## 2026-09-08
- did: Waveshare driver saved to Pico as epaper29.py (EPD_2in9_Landscape). display wired hat-style / direct pin.
- did: BUSY (GP13) reads 0 after a power cycle -> display alive.
- broke: init hangs on 'e-Paper busy' forever. suspect PULL_UP on BUSY in driver floating it high.
- next: fix display init. LED tabled. mic not wired.

## 2026-09-11
- status v0: MicroPython ok, buttons ok. display stuck on BUSY. LED tabled. mic unwired.
- planned: multi-list firmware, UP/DOWN scroll, ACTION tap check / hold delete, UP+ACTION voice. LED pulse/blink/double.
- housing ideas: calculator shell, pager shell, Altoids tin (tin maybe too tight for display).
- shelving v0. too many unknowns at once.
