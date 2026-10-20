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

## 2026-10-17
- P8 display v2: draw_picker() — 'Lists' header, dot on open list, unchecked count right side. shared _scroll/_highlight.
- apptest v3: two modes. DOWN+ACTION hold opens picker, ACTION opens list (blink), DOWN+ACTION again cancels.
- all non-voice features work.
- checkpoint: laptop died before the standalone step.
- next: display.py gets draw_message() + guarded sleep(); new app.py (apptest logic + 1 min idle display sleep); new main.py (auto-run on boot, hold UP at power-on = skip app, crash -> LED flicker + error on screen + error.log).
- then 4 tests: Run/Stop in Thonny, boot w/ Thonny fully closed, idle sleep, UP escape hatch.
- after that: voice mode (needs mic soldered).

## 2026-10-18
- P8 standalone: display v3 = draw_message() (error screen now, voice confirms later) + sleep() guarded (only if awake).
- app.py v1 = apptest v3 logic + idle: 1 min no press -> display deep sleep, list stays on screen, next press = 1 full refresh.
- main.py: auto-runs on power-up. hold UP at plug-in -> app skipped, onboard LED x3. crash -> traceback to error.log, LED flicker, error on screen.
- 4 tests pass: Run/Stop in Thonny, boot w/ Thonny fully closed, idle sleep, UP escape hatch. Aurelius = standalone device.
- sleep screen ("plaque"): big AURELIUS 4x-scaled from the built-in 8x8 font, white on black band w/ inner rules; background = tiled AURELIUS rows slid 36 px each, checkerboard-dithered to grey.
- 5 styles mocked (plaque / monolith / monolith AVRELIVS / weave / stack), plaque picked.
- display v4: saver() = draw plaque, full refresh, deep sleep. e-ink holds it w/ power pulled.
- app v2: idle -> saver(). first press after only wakes (redraws list or picker), no action -> no blind check-offs.
- 5 tests pass: plaque at ~1 min, wake press does nothing else, next press acts, plaque survives unplug, picker wakes back to picker.
- tip: IDLE_MS = 10000 while testing, back to 60000 after.
- P6: YIHUA 926 III arrived. 340 C, tip tinned. round INMP441 = 2x3 holes -> header snapped 3+3, breadboard jig, one corner tacked + checked flat, then rest. 6 clean cones.
- P6 wiring: mic straddles center gap ~rows 46-48 (no M-F jumpers), M-M from each pin row: SCK j20, WS j19, SD j17, VDD +, GND -, L/R -.
- P6 done: mictest bars jump on talk, spike on clap. raw level low-ish (INMP441 is quiet; voice mode adds software gain).
- next: voice mode (last P8 piece).
- voice decisions: STT local faster-whisper on Mac, AI = DeepSeek (OpenAI-compatible, swap later), push-to-talk.
- V1 recording: flash-write version hung inside readinto -> RAM buffer version (192 KB). 3.30 s audio / 3.33 s wall = no drops.
- playback via relay/pcm2wav.py + afplay = static. rawdump v1-v3 -> only top 8 bits arriving -> hardware. rewired + resoldered -> clean audio.
- full write-up: docs/audio-debug.md.
- next: V2 upload rec to relay /voice.

## 2026-10-19
- V4 (Mac only, no Pico): relay/voice_ops.py = transcript + lists.json -> DeepSeek (deepseek-v4-flash, JSON mode) -> validate() -> {"ops", "say"}.
- ops map 1:1 onto lists.py: add / check / uncheck / delete / clear_done / new_list / switch / rename_list / delete_list.
- validate() replays every op on a copy of the real lists: fuzzy names snap to exact spelling, impossible ops dropped w/ reason, ASCII fold for the 8x8 font. confirm line built in code, <= 36 chars.
- key in ~/aurelius-relay/.env (gitignored), openai pkg in the relay venv.
- test_ops.py: --offline 13/13 (fake model replies). live 14/14 correct, 0.8-2.8 s each.
- watch: "at mail professor" -> checked off Email professor. reversible, left as is.

## 2026-10-20
- V2: Pico -> relay upload. net.py v1 = raw socket POST /voice, body = lists.json + PCM, X-State-Len header splits them. BUF sent as 4 KB memoryview slices, never copied (MemoryError lesson, #26). server v2 saves clips/*.wav.
- vtest.py: wifi ok, free RAM 248672, 3.07 s clip, WAV plays back clean on the Mac.
- V3: stt.py, faster-whisper base.en, int8 CPU. first run crashed: PyAV 19 rejects faster-whisper's metadata_errors arg -> read WAV w/ wave + numpy, PyAV skipped. 0.6 s for "Add batteries to lab." model download 43 s once, then 1.3 s load.
- server v3: /voice = save WAV -> STT -> voice_ops -> reply. whisper loads at startup.
- full loop from vtest: "Add Morning Run to my to-do list." -> add op back in 3180 ms.
- V5: voicecmd.py (record -> upload -> apply ops via lists.py), app v3 (UP+ACTION = real voice, _settle() drains buttons after), display v5 toast() banner, net v2 (wifi joins at boot, 15 s timeout).
- NameError 'voice' in app.py run() = new app.py not actually on the Pico. re-pasted whole file from the Pico copy -> fixed.
- V5 table 9/9 incl. standalone w/ Thonny closed. voice works.
- "Open my list." -> "No list name given" (Whisper drops the s, no op for the picker). added show_lists op + fast path phrases (singular/plural) that skip the AI.
- sleep op: "sleep", "goodnight", "go to bed", ... fast path, 0.0 s AI. combined ("add milk and go to sleep") via DeepSeek. voicecmd v2, app v4, voice_ops v2.
- snags: commands pasted into the running relay window, Terminal blocked from ~/Downloads, replugged w/ UP held (escape hatch) -> looked stuck on plaque.
- breadboard Aurelius = fully functional. P8 done.
- full write-up w/ code: docs/voice-pipeline.md.
- next: P9 portable power.
