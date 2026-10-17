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

## 2026-09-26
- P3: BUSY quick check read 1 (bad sign).
- fix: busy_diag -> pull-down 1, pull-up 1, after reset 0. display IS powered, just boots stuck busy. one RST pulse -> idle. driver init() resets anyway.
- likely the whole v0 hang.
- P3: ReadBusy patched w/ 5 s timeout -> RuntimeError instead of frozen Pico. demo ran: text, shapes, 0-9 partials, gray bands, sleep.

## 2026-09-27
- P3 done: hello.py draws AURELIUS / UU002 - Unumusu Laboratory. unplugged, text stays. the wall from v0 is down.

## 2026-09-29
- P4: buttons rows 24-36, diagonal wiring (works any rotation). below the Pico so nothing shorts Pico pins.
- P4 done: each prints own name pressed/released, no crosstalk, quiet when idle. zero rework vs v0.

## 2026-10-01
- P5: blue 5 mm LED + 220 ohm on GP15, rows 40-42.
- P5 done: blinks x3, PWM breathing smooth.

## 2026-10-03
- recap P1-P5: Pico alive, rails live, display draws + holds, 3 buttons clean, LED blinks + breathes.
- next: P6 mic -> P7 Wi-Fi + relay -> P8 firmware.

## 2026-10-05
- syscheck.py: one-click check (LEDs, 5 s button window, display). passed after the board sat a while.

## 2026-10-07
- P6: INMP441 = round board w/ 6 holes + a LOOSE 6-pin header. has to be soldered. no iron -> P6 blocked.
- mictest.py written, UNTESTED. skipping to P7.

## 2026-10-08
- P7: network = iPhone hotspot (Pico = 2.4 GHz only, no eduroam).
- broke: SSID mismatch -> renamed phone to JacobsiPhone. still status -2.
- fix: Personal Hotspot screen open + Maximize Compatibility ON + Allow Others toggle. wifiscan showed it. Pico connected.

## 2026-10-09
- P7: relay on the Mac, ~/aurelius-relay, venv, FastAPI + uvicorn. /health works at localhost:8000.

## 2026-10-11
- P7: Mac on same hotspot, IP from `ipconfig getifaddr en0`, RELAY_URL set in config.py.
- P7 done: Pico prints 200 {"status":"ok","relay":"Aurelius"}, Terminal logs GET /health.

## 2026-10-12
- P8: soldering station picked (YIHUA 926 III) so P6 can resume later.
- P8 lists.py: lists.json on flash, save after every change, write tmp then swap (power cut never leaves half a file). buttons use index, voice will use find(text).
- liststest: To-do -> Groceries, Eggs [ ], Milk [x], Rice deleted.

## 2026-10-13
- P8: power-cycle check. lists.json survived: Groceries current, Eggs unchecked, Milk checked.

## 2026-10-14
- P8 display.py v1: black header (name + done/total), 7 rows, checkbox, strike-through, inverse highlight, scrollbar, '..' truncation.
- partial refresh for moves, full every 10 to clear ghosting.
- displaytest: builds a 10-item 'Test' list, scrolls through. worked first try. like the look, may restyle later.

## 2026-10-15
- P8 buttons.py: events UP, DOWN, ACTION, ACTION_LONG, UP+ACTION, DOWN+ACTION. debounce 30 ms, hold 800 ms.
- taps fire on RELEASE so a combo never starts as a tap. holds fire once while held.
- navtest: every case in the table behaves.
- P8 apptest v1: ACTION tap toggles, ACTION hold deletes, highlight lands on next (or prev if last). each change saved.
- persistence across power cycle ok.

## 2026-10-16
- P8 led.py: background Timer every 20 ms plays (brightness, ticks) patterns -> LED keeps going during screen refresh. blink / double / flicker / pulse(loop).
- apptest v2: blink on check (not uncheck), double on delete, UP+ACTION toggles pulse (voice preview).
