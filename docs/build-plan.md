# build plan — Aurelius (UU002)

shorthand copy of the restart build doc (full version = "Aurelius (UU002) — Build Document" in the Unumusu Laboratory project files).

## vision
- a to-do list that gets picked up, used, put down. tech that complements life, doesn't take from it.
- Unumusu = antithesis of screen-captured life. Jobs-era "tech assists everyone" kept, the pull removed.
- Unum Usum: lists only. no feeds / notifs / apps / browsing. every part + feature must serve the one use.
- e-ink = the point, not a compromise. no backlight, holds image w/ 0 power, too slow for feeds.
- AI only when summoned (button hold). answer = list changes, not a conversation.
- minimalism = restraint (fewer functions), not polish. handmade housings from repurposed casings. Latin names.

## what it does
- 2.9" e-ink, 296x128 landscape. header = list name + count. ~7 rows. selected row highlighted.
- controls:

| input | action |
| --- | --- |
| UP | selection up |
| DOWN | selection down |
| ACTION tap | check / uncheck |
| ACTION hold ~1 s | delete item |
| UP + ACTION hold | voice mode |
| DOWN + ACTION hold | list picker (was "proposed") |

- LED language: slow pulse = voice (listening/thinking). single blink = checked. double blink = deleted. rapid flicker = failure (e.g. no Wi-Fi).
- voice: hold UP+ACTION, speak, release -> audio + lists to relay -> AI -> list ops -> one-line confirm. no speaker.
  - e.g. "add eggs, milk, rice to groceries" / "new list called packing" / "break 'finish lab report' into steps" / "clear everything checked off"

## system
- buttons (GPIO) + mic (I2S) -> Pico 2 W -> e-ink (SPI) + LED (GPIO)
- LiPo -> charger + switch -> VSYS
- Wi-Fi only in voice mode -> relay server on laptop (STT then LLM) -> list ops back

## phases
1. Pico alive (MicroPython, Thonny, onboard LED)
2. breadboard rails (3V3 + GND both sides)
3. display (8 wires, driver, demo, own text survives unplug)
4. buttons (0 held / 1 released, no crosstalk)
5. LED (blink + PWM pulse)
6. mic (I2S, values ~0 silent, jump w/ noise)
7. Wi-Fi + relay (Pico prints relay /health reply)
8. firmware: list storage -> screen drawing -> button nav -> check/delete -> LED patterns -> list switching -> voice LAST
9. portable power (batt -> charger -> switch -> diode -> VSYS)
10. perfboard + housing (survives a week in pocket/bag)

## firmware architecture
| file | job |
| --- | --- |
| main.py | runs on boot, main loop |
| config.py | wifi, relay URL, constants |
| epd_2in9.py | Waveshare driver (+ fixes only) |
| display.py | header, items, selection, confirmations |
| buttons.py | debounce, short/long, 2-button holds |
| led.py | blink, double, pulse, flicker |
| lists.py | load/save/add/check/delete/switch |
| voice.py | record to flash, upload, apply reply |

data model `lists.json`:
```json
{"current": "Groceries",
 "lists": {"Groceries": [{"text": "Eggs", "done": false}, {"text": "Rice", "done": true}],
           "Lab": [{"text": "Finish report", "done": false}]}}
```
modes: list view / list picker / listening / thinking.

rules:
- save lists.json after EVERY change
- debounce ~30 ms, long press ~800 ms
- partial refresh for scrolling, full every ~10 to clear ghosting
- Wi-Fi off except voice mode
- every wait gets a timeout (incl. display BUSY loop)

## voice pipeline (planned)
- why relay: Pico = 520 KB RAM, no model fits. keeps API keys off device. swap AI w/o reflash.
- 1. hold UP+ACTION -> record 16 kHz 16-bit mono (~32 KB/s) TO FLASH FILE (6 s ~ 190 KB)
- 2. release -> Wi-Fi on -> upload audio + lists.json
- 3. relay STT: local faster-whisper (private) or cloud API
- 4. text + lists -> LLM (hosted API), instructed: reply ONLY w/ list ops JSON
- 5. Pico applies, saves, 1-line confirm, Wi-Fi off
- reply format:
```json
{"ops": [{"op": "add", "list": "Groceries", "items": ["Eggs", "Milk"]},
         {"op": "check", "list": "Lab", "item": "Finish report"},
         {"op": "new_list", "list": "Packing"}],
 "message": "Added 2 to Groceries"}
```
- allowed ops: add, check, uncheck, delete, new_list, delete_list, rename, clear_done. anything else rejected.
- relay endpoints: /health (done), /voice (done).
- Pico 2 W = 2.4 GHz only, no eduroam/enterprise login -> phone hotspot.

## power + enclosure (planned)
- batt -> charger out -> slide switch -> Schottky -> VSYS (pin 39), grounds joined. diode stops USB vs batt fight.
- battery life order: Wi-Fi only in voice > light sleep between presses > deep sleep when idle (screen keeps list).
- measure real draw w/ USB power meter -> picks battery size.
- housing candidates: calculator shell / pager shell / Altoids tin (tin maybe tight for display). decide after breadboard works.
  - measure stack height (display, Pico, perfboard, batt)
  - openings: screen, 3 buttons, mic hole, LED, USB charge
  - metal housing -> insulate (Kapton), expect weaker Wi-Fi
  - salvaged parts -> parts bin, not trash

## open decisions
- [x] voice: push-to-talk (record while held) — built
- [x] list switching: DOWN+ACTION hold -> picker screen (built)
- [x] STT: local faster-whisper base.en on the Mac (0.5-0.7 s/clip)
- [ ] relay long-term home: laptop / always-on machine / cloud
- [ ] checked items: stay until cleared vs vanish after a day
- [ ] housing
