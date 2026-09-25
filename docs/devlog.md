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

## 2026-09-15
- restart from scratch, same parts. vision sharper: Unumusu = antithesis of screen-captured life. e-ink central. minimalism = restraint not polish.
- did: full build plan — vision, controls, LED language, phases 1-10, firmware files, lists.json model, voice pipeline via relay, power, housing, open decisions.

## 2026-09-17
- did: pin map. display GP8-13, buttons GP2-4, LED GP15, mic GP16-18. no shared signal pins. 3V3 = pin 36 only.

## 2026-09-19
- P1: MicroPython already on it, v1.28.0, Pico 2 W w/ RP2350. no reflash needed.
- P1: reflashing doesn't delete files -> wipe() everything from v0. onboard LED toggles.
- P1 done: blink.py saved ON the Pico ([brackets] on tab), blinks x10, prints 'Aurelius: Pico alive'.

## 2026-09-22
- P2: Pico seated c1-c20 / h1-h20. j5 -> right +, j3 -> right -, bridged to left rails.
- P2 done: no multimeter -> GP0 test, left + = 1, left - = 0.

## 2026-09-24
- P3: board = Pico-ePaper-2.9, V2, B/W. driver = Pico_ePaper-2.9.py (has init_4Gray). saved to Pico as epd_2in9.py.
- P3: using the 8-pin cable instead of seating on the hat -> Pico stays on breadboard for everything else.
- P3: BS jumper on 0. wired b11-b17.
