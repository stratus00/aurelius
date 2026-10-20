# Aurelius (UU002)

Unumusu Laboratory device #002 — physical to-do list. e-ink screen, 3 buttons, one LED, voice requests turned into list changes by an AI on a relay server. Unum Usum: One Use.

## status
| phase | what | state |
| --- | --- | --- |
| 1 | Pico alive (MicroPython v1.28, Thonny) | done |
| 2 | breadboard rails | done |
| 3 | e-ink display | done |
| 4 | buttons | done |
| 5 | LED | done |
| 6 | INMP441 mic | done — headers soldered, mictest passes |
| 7 | Wi-Fi + relay | done |
| 8 | firmware | done — lists / screen / nav / check+delete / LED / list picker / standalone boot / plaque sleep screen / voice (push-to-talk -> relay -> local STT -> DeepSeek -> list ops) |
| 9 | portable power | next |
| 10 | perfboard + housing | not started |

## layout
| path | what |
| --- | --- |
| `firmware/` | files that live on the Pico as the app (`main.py`, `app.py`, `lists.py`, `display.py`, `buttons.py`, `led.py`, `voice.py`, `voicecmd.py`, `net.py`, `screensaver.py`, `epd_2in9.py`, `config.example.py`) |
| `tests/` | test scripts saved on the Pico, one per step (`liststest.py`, `navtest.py`, `apptest.py`, ...) |
| `snippets/` | one-off Shell commands (wipe, rail test, BUSY diag, wifi scan, ...) |
| `relay/` | FastAPI relay that runs on the Mac: `/health`, `/voice` (`server.py`), speech-to-text (`stt.py`), transcript -> list ops (`voice_ops.py`), tests (`test_ops.py`) |
| `docs/` | `devlog.md` (what happened), `mistakes.md` (what broke + fix), `voice-pipeline.md` (V2-V5: how voice works + every issue w/ code), `audio-debug.md` (mic audio troubleshooting, first person), `build-plan.md`, `pinmap.md`, `wiring.md`, `bom.md` |

old versions of a file = `git log -p <file>` (e.g. `display.py` v1 list-only -> v2 + picker; `apptest.py` v1 -> v3; `app.py` v1 -> v4 voice; `net.py` v1 -> v2).

## on the Pico
copy everything in `firmware/` + whichever `tests/` script is needed. `config.example.py` -> `config.py` with the real hotspot password + current Mac IP (gitignored).
`main.py` runs the app on power-up. hold UP while plugging in = skip the app (to get into Thonny).
voice needs the relay running on the Mac, same hotspot — see `relay/RELAY.md`.

## controls
UP / DOWN move. ACTION tap = check/uncheck. ACTION hold = delete. DOWN+ACTION hold = list picker. UP+ACTION hold = voice: LED breathes -> talk -> release -> list updates + one-line banner, LED blinks.

## voice examples
- "add batteries" / "add bread, butter and eggs to groceries"
- "I called the dentist" / "check off milk and yogurt" / "remove laundry"
- "clear the done stuff on groceries"
- "make a camping list with tent and lantern" / "rename lab to workbench" / "show me groceries"
- "open my lists" -> picker. "sleep" / "goodnight" -> plaque screen (both skip the AI)
