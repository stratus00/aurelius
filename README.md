# Aurelius (UU002)

Unumusu Laboratory device #002 — physical to-do list. e-ink screen, 3 buttons, one LED, voice requests turned into list changes by an AI on a relay server. Unum Usum: one use, done right.

## status
| phase | what | state |
| --- | --- | --- |
| 1 | Pico alive (MicroPython v1.28, Thonny) | done |
| 2 | breadboard rails | done |
| 3 | e-ink display | done |
| 4 | buttons | done |
| 5 | LED | done |
| 6 | INMP441 mic | **blocked** — header needs soldering (station ordered) |
| 7 | Wi-Fi + relay | done |
| 8 | firmware | lists / screen / nav / check+delete / LED / list picker done. next: standalone boot (`app.py` + `main.py`), then voice |
| 9 | portable power | not started |
| 10 | perfboard + housing | not started |

## layout
| path | what |
| --- | --- |
| `firmware/` | files that live on the Pico as the app (`lists.py`, `display.py`, `buttons.py`, `led.py`, `epd_2in9.py`, `config.example.py`) |
| `tests/` | test scripts saved on the Pico, one per step (`liststest.py`, `navtest.py`, `apptest.py`, ...) |
| `snippets/` | one-off Shell commands (wipe, rail test, BUSY diag, wifi scan, ...) |
| `relay/` | FastAPI relay that runs on the Mac (`/health` only so far) |
| `docs/` | `devlog.md` (what happened), `mistakes.md` (what broke + fix), `build-plan.md`, `pinmap.md`, `wiring.md`, `bom.md` |

old versions of a file = `git log -p <file>` (e.g. `display.py` v1 list-only -> v2 + picker; `apptest.py` v1 -> v3).

## on the Pico
copy everything in `firmware/` + whichever `tests/` script is needed. `config.example.py` -> `config.py` with the real hotspot password (gitignored).
currently run `tests/apptest.py` from Thonny for the full non-voice app.

## controls
UP / DOWN move. ACTION tap = check/uncheck. ACTION hold = delete. DOWN+ACTION hold = list picker. UP+ACTION hold = voice (preview: LED pulse).
