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
| 17 | P8 | list empty in the next test | deleted every item during the delete test | snippets/refill_test_list.py |
| 18 | P8 | standalone step not started | laptop died | checkpoint logged, resumed 10-18, all 4 standalone tests pass |
| 19 | P8 | (design catch) waking from the sleep screen could check off an item | list hidden behind plaque, but the wake press still went to list_view | app v2: first press after the saver only redraws. caught before flashing |
| 20 | P8 | can't save files from Thonny while app runs | main.py running on the Pico | Stop first, save, then Run main.py or replug w/ Thonny closed |
| 21 | P6 | header strip didn't match the mic | round INMP441 has 2x3 holes, not 1x6 | snap header into two 3-pin pieces. breadboard placement must straddle the gap or pins short |
| 22 | P6 | planned M-F jumpers, had none | wiring plan assumed mic off-board | mic on breadboard across the gap, M-M jumpers from each pin's row |
| 23 | P6 | sharp conical tip swap | wanted precision | small chisel (0.8D/1.2D) heats pin + pad better; swap tips cold, tin new tip immediately |
| 24 | P8 voice | rectest hangs after LED, Thonny Stop does nothing | flash writes every 32 ms pause interrupts -> I2S stream stalls -> readinto waits forever | record into a 192 KB RAM buffer, write file only after mic off. escape hatch (hold UP at plug-in) to get back in |
| 25 | P8 voice | SyntaxError line 31 after a one-line edit | paste broke the line | replace whole file instead of patching one line |
| 26 | P8 voice | MemoryError allocating 160768 bytes | `BUF[:n]` slice = full copy | viper peak() scans in place |
| 27 | P8 voice | peak 32768 | mic startup spike (~85 ms), only 32 ms skipped | skip ~200 ms (6 reads) |
| 28 | P6/P8 | playback = loud static, faint voice; mictest had looked fine | marginal SD joint/contact: only top ~8 bits arrived (run of 1s then 0s). + RP2350-E9 pull-down latch on the silent R slot | rawdump v1-v3 to locate, rewired mic rows 46-48 w/ exact holes + resoldered -> 512/512 real words, clean audio. lesson: test what the next stage needs (listen), dump raw data |
| 29 | P8 V4 | `pip3 install openai` -> unclear where it goes | relay has its own venv, system pip != .venv | `source .venv/bin/activate` first (prompt shows `(.venv)`), then `pip install`. new Terminal window = activate again |
| 30 | P8 V4 | `echo 'DEEPSEEK_API_KEY=...'` printed the line, saved nothing | missing `> .env` | `echo '...' > .env`, check w/ `cat .env`. (watch) key showed in a screenshot -> rotate it on platform.deepseek.com |
| 31 | P8 V4 | (watch) "at mail professor" -> checked off Email professor | STT garble + model guessed the intent | left as is (check is reversible). tighten the prompt if it happens w/ real speech |
| 32 | P8 V4 | banner `New list, 1 items` / `Added 1 items` | plural hardcoded | `(" item" if n == 1 else " items")` |
| 33 | P8 V3 | `TypeError: open() got an unexpected keyword argument 'metadata_errors'` | faster-whisper 1.2.1 calls `av.open(..., metadata_errors="ignore")`, pip pulled PyAV 19.0.0 which doesn't take it | stt.py `load_wav()`: wave + numpy -> float32 array -> `transcribe()`. PyAV never used. voice-pipeline.md #3 |
| 34 | P8 V3 | first run `model loaded in 43.1 s` + `HF_TOKEN` warning | one-time base.en download (~150 MB) | harmless. next load 1.3 s. relay loads the model at startup |
| 35 | P8 V5 | `NameError: name 'voice' isn't defined` (app.py line 89, in run) | new app.py never made it onto the Pico | open app.py FROM the Pico, Cmd+A, paste whole file, Cmd+S, check line 1 ends `sleep screen, voice`. same lesson as #25 |
| 36 | P8 V5 | "Open my list." -> `No list name given` / `Which list? Name unclear` | Whisper drops the s + no op for the picker, model hunted for a list name | `show_lists` op + `SHOW_PHRASES` fast path (no AI call). voice-pipeline.md #5 |
| 37 | relay | pasted commands (incl. `# Ctrl+C first`) into the relay window, nothing ran | uvicorn owns that Terminal while running; `#` lines are notes | Ctrl+C, wait for `%`, then run. 2nd window for everything else |
| 38 | relay | `ls: ~/Downloads: Operation not permitted`, `mv: No such file or directory` | macOS privacy blocks Terminal from Downloads; files also never downloaded | files put straight into ~/aurelius-relay. alt: Privacy & Security -> Files and Folders -> Terminal -> Downloads |
| 39 | P8 V5 | after replug, stuck on the plaque screen | UP held while plugging in = escape hatch -> app skipped; e-ink keeps the last image w/o power | replug w/o touching buttons. onboard LED x3 = app skipped |
| 40 | P8 V5 | (design catch) long voice hold could leave queued button events -> stray check/delete after a command | buttons not polled during record + upload (~3-5 s) | `_settle()`: wait for all buttons up, drain `poll()` 200 ms |
| 41 | P8 V2 | (design catch) upload w/ `requests` would copy the 192 KB buffer | same copy as #26 | raw socket, `sendall()` 4 KB `memoryview` slices |
| 42 | P8 V4 | (design catch) model can return lists/items that don't exist, misspelled, non-ASCII | STT + LLM errors | `validate()` replays ops on a copy: fuzzy match, drop impossible ops, ASCII fold, banner built in code |
