# mistakes

symptom -> cause -> fix. v0 = first attempt (shelved). numbers = restart.

| # | phase | symptom | cause | fix / lesson |
| --- | --- | --- | --- | --- |
| v0-1 | v0 buttons | buttons stuck / wrong reads | not bridging the center gap -> legs shorted on one side | straddle gap e<->f, signal e side, GND f side. lesson: exact coords, not vague placement |
| v0-2 | v0 display | init hangs on "e-Paper busy" forever | suspected driver PULL_UP on BUSY; never solved in v0 | real cause found in restart (#7): display boots stuck busy, needs RST pulse. + no timeout in ReadBusy = frozen Pico (#8) |
| v0-3 | v0 display | lots of guessing on hat/socket pin mapping | socket is a mirror image of the Pico seen from behind | restart: use the 8-pin cable connector, no mirror mapping |
| v0-4 | v0 LED | LED circuit never built | stalled on display first | restart: LED done first try in P5 |
| v0-5 | v0 overall | build stalled | too many new things at once, no per-step proof | restart rule: one part at a time, prove alone, "done when" check per step, test scripts saved |
| 1 | P1 | SyntaxError in Shell, wipe output cut off | pasted into wrong place | rerun `import os; os.listdir()` to confirm clean. reflash != wipe |
| 2 | P1 | ran blink code, thought it was saved | ran in the Shell -> runs on Pico, saves nothing | editor -> File > Save as > Raspberry Pi Pico. [brackets] on tab = on Pico |
| 3 | P1 | blink code ended up at bottom of the old driver file | old v0 Pico_ePaper-2.9.py tab still open; `*` = unsaved | close tab, Don't Save, Cmd+N for a new tab |
| 4 | P2 | rail test line errored after replug | replug restarts the Pico, wipes the earlier `from machine import Pin` | import + call on ONE line |
| 5 | P3 | which driver file? | repo has -B (B/W/red), _D, -C, -B_V4 variants | V2 B/W -> Pico_ePaper-2.9.py. rename to epd_2in9.py — hyphen can't be imported |
| 6 | P3 | seat display on Pico or use cable? | - | cable. seating pulls Pico off breadboard = dead end. seating only as a diagnostic if wiring fails |
| 7 | P3 | BUSY reads 1 before demo | display powered but stuck busy from power-up | busy_diag 1/1/0 -> RST pulse -> idle. driver resets on init -> demo works |
| 8 | P3 | stock ReadBusy loops forever if BUSY stuck | no timeout in Waveshare driver | 5 s timeout. NOTE: file has 2 ReadBusy (Portrait + Landscape). Cmd+F lands on Portrait first; Landscape is the one used -> make sure the Pico copy has BOTH patched (repo copy does) |
| 9 | P5 | which LED? | - | single-color 2-leg 5 mm. blue + 220 ohm = dim calm glow. 4-leg RGB needs 3 pins, skip. 220 ohm = red-red-brown |
| 10 | P6 | Thonny: port /dev/cu.usbmodem142201 no longer exists | Pico got a new port name after replug | bottom-right > Configure interpreter > auto-detect port > Stop. no usbmodem at all -> unplug, look for 3V3-GND short |
| 11 | P6 | can't wire the mic | INMP441 header ships unsoldered | P6 blocked, moved to P7. tilt-header trick = 10 s test only, not reliable |
| 12 | P7 | SSID never matched | iPhone name used a curly ’ not a typed ' | renamed phone to JacobsiPhone. caps count. quotes = Python string, not part of name |
| 13 | P7 | wifitest status -2 w/ right name | iPhone only broadcasts hotspot while its screen is open; 5 GHz unless Maximize Compatibility | keep Personal Hotspot screen open, Maximize Compatibility ON, toggle Allow Others. wifiscan.py to see what Pico hears |
| 14 | P7 | (watch) RELAY_URL goes stale | Mac IP changes each hotspot session | re-run ipconfig getifaddr en0 every session before relaytest |
| 15 | P8 | Thonny "Internal error" popup, `<no backend>` | unplugged for the power-cycle test, Thonny never reconnected, typed into a dead Shell | click `<no backend>` -> MicroPython (Raspberry Pi Pico) or Stop. wait for >>> before typing. queued command ran twice after reconnect (harmless) |
| 16 | P8 | (known limit) very fast taps can drop | buttons not polled during ~0.5 s e-ink refresh | fine at normal speed. interrupts later if it becomes a problem |
