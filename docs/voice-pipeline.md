# Voice pipeline (V2–V5)

Hold UP+ACTION, talk, release -> list changes on the e-ink screen. ~3 s round trip for a 3 s clip.
Every problem hit while building it, with the code that fixed it. File:line refs = repo state at the end of V5.

## flow

```
Pico                                         Mac relay (~/aurelius-relay)
----                                         ----------------------------
app.py      UP+ACTION hold (800 ms)
voicecmd.py led.pulse() + voice.record()  -> 16 kHz 16-bit mono PCM in 192 KB RAM buffer
net.py      post_voice(): raw socket      -> server.py  POST /voice
              body = lists.json + PCM                   save clips/YYYYMMDD-HHMMSS.wav
                                                         stt.py       faster-whisper base.en  (0.5-0.7 s)
                                                         voice_ops.py fast path (sleep / show lists)  (0.0 s)
                                                                      else DeepSeek JSON mode (0.8-2.8 s)
                                                                      -> validate() against the real lists
            {"ops", "say", "heard"}       <-
voicecmd.py _apply() each op -> lists.py (saved to flash)
app.py      redraw list / picker / plaque + display.toast(say), LED blink
```

## wire format

`net.post_voice()` sends one HTTP/1.0 POST. `X-State-Len` = byte length of the JSON at the front of the body, rest = PCM.

```
POST /voice HTTP/1.0
Content-Length: <json + pcm>
X-State-Len: <json bytes>

{"current": "To-do", "lists": {...}}<raw PCM>
```

relay splits it (`relay/server.py:19-21`):
```python
n = int(request.headers.get("x-state-len", "0"))
state = json.loads(body[:n] or b"{}")
pcm = body[n:]
```

reply:
```json
{"ops": [{"op": "add", "list": "To-do", "text": "Morning run"}], "say": "Added Morning run (To-do)", "skipped": [], "heard": "Add Morning Run to my to-do list."}
```

## ops

| op | fields | Pico does |
| --- | --- | --- |
| add | list, text | `lists.add(text, list)` |
| check / uncheck | list, item | `lists.set_done(find(item), True/False, list)` |
| delete | list, item | `lists.delete(find(item), list)` |
| clear_done | list | `lists.clear_done(list)` |
| new_list | name | `lists.new_list(name)` |
| switch | name | `lists.switch(name)` |
| rename_list | name, new | `lists.rename_list(name, new)` |
| delete_list | name | `lists.delete_list(name)` (never the last list) |
| show_lists | - | opens the list picker |
| sleep | - | plaque screen + display deep sleep |

banner (`say`) is built in code from what actually got applied, never written by the model, <= 36 chars (`SAY_MAX`, `relay/voice_ops.py:33`).

---

## 1. V4 — the model's output can't be trusted as-is

**problem.** two error sources stack: speech-to-text garbles words, and the model can return names that aren't on the device (misspelled list, item that doesn't exist, curly quotes / accents the 8x8 font can't draw). an op naming a missing item would crash or silently do nothing on the Pico.

**fix.** the relay replays every op on a deep copy of the Pico's lists before sending anything back. ops that can't apply get dropped with a reason; names get snapped to the exact spelling on the device.

`relay/voice_ops.py:285-296`
```python
def validate(raw, state):
    """Model reply -> {"ops": [...], "say": str, "skipped": [...]} (ops guaranteed to apply)."""
    s = copy.deepcopy(state)
    ops, skipped = [], []
    raw_ops = raw.get("ops") if isinstance(raw, dict) else None
    for op in (raw_ops if isinstance(raw_ops, list) else [])[:MAX_OPS]:
        clean, why = _check(op, s)
        if clean:
            _apply(clean, s)
            ops.append(clean)
        elif why:
            skipped.append(why)
```

- `_match()` (`:134`): exact case-insensitive first, then `difflib` closest at 0.6 -> "grocery" -> `Groceries`, "call the dentist" -> `Call dentist`.
- `_ascii()` (`:127`): NFKD fold + drop non-ASCII -> "Crème brûlée — café" -> `Creme brulee cafe`.
- re-adding a done item = un-check it (`:174`). new_list on an existing name = switch to it (`:190`).
- JSON mode can return empty content -> one retry (`:107`, `response_format={"type": "json_object"}` at `:111`).

**result.** offline suite (fake model replies, no API) passes; live suite against DeepSeek 14/14 correct, 0.8-2.8 s each.

| said | ops back | banner |
| --- | --- | --- |
| add bread, butter, and orange juice to the grocery list | 3x add Groceries | `Added 3 items` |
| um I called the dentist | check Call dentist | `Done: Call dentist` |
| check off milk and yogurt | check Milk, check Greek yogurt | `Checked off 2` |
| make a new list called camping and put tent and sleeping bag on it | new_list, 2x add, switch | `New list, 2 items` |
| add eggs to groceries (Eggs already done) | uncheck Eggs | `Undone: Eggs (Groceries)` |
| delete the laundry list (no such list) | - | `No list named Laundry` |
| what time is it | - | `Not a list command` |
| at mail professor | check Email professor | `Done: Email professor` (watch: guessed) |

small bug caught here: banner said `New list, 1 items` / `Added 1 items` -> plural fixed: `(" item" if n == 1 else " items")`.

## 2. V2 — uploading 192 KB without copying it

**problem.** `requests.post(data=...)` wants a bytes object. `voice.BUF[:nbytes]` is a full copy, and a copy that size already caused `MemoryError: memory allocation failed, allocating 160768 bytes` in V1 (mistakes #26). free RAM with Wi-Fi up: 248672 bytes.

**fix.** raw socket, HTTP written by hand, audio sent as 4 KB `memoryview` slices of the buffer. no copy ever made.

`firmware/net.py:49-53`
```python
        s.sendall(head.encode())
        s.sendall(st)
        mv = memoryview(pcm)
        for i in range(0, len(mv), 4096):
            s.sendall(mv[i:i + 4096])
```
caller passes a view, not a slice copy (`firmware/voicecmd.py:61`):
```python
res = net.post_voice(lists.data, memoryview(voice.BUF)[:nbytes])
```
- Wi-Fi power save off (`w.config(pm=network.WLAN.PM_NONE)`) -> faster upload.
- HTTP/1.0 -> server closes the connection after the reply, so the read loop just runs until `recv()` returns empty.

**result (tests/vtest.py).**
```
1. wifi...
   ok, free RAM: 248672
4. recorded 3.07 s, uploading...
5. reply in 3180 ms: {'heard': 'Add Morning Run to my to-do list.', 'ops': [{'text': 'Morning run', 'op': 'add', 'list': 'To-do'}], 'say': 'Added Morning run (To-do)', 'skipped': []}
```
(that run already had V3 + V4 behind `/voice`. V2 alone returned `{"say": "Got 2.3 s"}` and a playable WAV in `clips/`.)

## 3. V3 — faster-whisper crashed on its own audio decoder

**symptom.** first `python3 stt.py clips/*.wav`:
```
model loaded in 43.1 s
  File ".../faster_whisper/audio.py", line 46, in decode_audio
    with av.open(input_file, mode="r", metadata_errors="ignore") as container:
TypeError: open() got an unexpected keyword argument 'metadata_errors'
```

**cause.** `pip install faster-whisper` pulled faster-whisper 1.2.1 + PyAV (`av`) 19.0.0. faster-whisper passes `metadata_errors=` to `av.open()`; that PyAV build doesn't accept it. version clash between two packages pip picked, nothing in the Aurelius code.

**fix.** skip PyAV entirely. the clips are already plain 16 kHz mono 16-bit WAV (the relay writes them), so read the samples with the stdlib `wave` module and hand faster-whisper a float32 array. faster-whisper only calls `decode_audio()` when given a path.

`relay/stt.py:16-23`
```python
def load_wav(path):
    with wave.open(str(path), "rb") as w:
        pcm = w.readframes(w.getnframes())
    return np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768.0

def transcribe(path):
    segs, _ = model().transcribe(load_wav(path), language="en", beam_size=1)
    return " ".join(s.text.strip() for s in segs).strip()
```
**result.**
```
model loaded in 1.3 s
0.6 s  clips/20261020-114628.wav: Add batteries to lab.
```
- 43.1 s on the first run = one-time ~150 MB download of `base.en` from the HF hub. `HF_TOKEN` warning = unauthenticated download, harmless.
- pip pulled `x86_64` wheels (Intel-mode Python). still 0.5-0.7 s per clip, fine.
- model loads once at relay startup (`relay/server.py:9`, `stt.model()`) so the first voice command isn't slow.

## 4. V5 — `NameError: name 'voice' isn't defined`

**symptom.** first run of `main.py` after the V5 files:
```
Traceback (most recent call last):
  File "<stdin>", line 14, in <module>
  File "app.py", line 89, in run
NameError: name 'voice' isn't defined
```
then the error screen (main.py crash handler) redrew.

**cause.** the new `app.py` never references a name `voice` inside `run()`; the V5 version imports `voicecmd`, not `voice`. so the `app.py` on the Pico wasn't the new file — the paste didn't land in the Pico copy (old/mixed file still there).

**fix.** File -> Open -> Raspberry Pi Pico -> `app.py`, Cmd+A, paste the complete file, Cmd+S. check line 1:
```python
# app.py — Aurelius: list view, list picker, LED feedback, sleep screen, voice
```
same lesson as mistakes #25: replace whole files, don't patch.

## 5. V5 — "Open my list." -> `No list name given`

**symptom.** relay log:
```
[voice] 1.9 s clip | stt 0.5 s: "Open my list." | ai 2.2 s -> No list name given
[voice] 2.9 s clip | stt 0.7 s: "Open my list." | ai 2.3 s -> Which list? Name unclear
[voice] 2.0 s clip | stt 0.5 s: "Open grocery list." | ai 2.8 s -> -> Groceries
```
**cause.** two things. (a) there was no op for "show me all my lists" — the picker only opened with DOWN+ACTION — so the model went looking for a list name to `switch` to. (b) Whisper hears "list", not "lists", so even after adding the op a rule keyed on "my lists" could miss.

**fix.** new op `show_lists` -> Pico opens the picker. plus a fast path on the relay: plain phrasings never reach DeepSeek at all (0.0 s AI time, no tokens), singular or plural.

`relay/voice_ops.py:307-312`
```python
# "open my list", "show all lists", "go to my lists" ... (speech-to-text often drops the s)
SHOW_PHRASES = {
    (v + " " + o).strip()
    for v in ("", "open", "show", "show me", "go to", "see", "view", "back to")
    for o in ("my lists", "my list", "lists", "all lists", "all my lists", "the lists", "list of lists")
}
```
`relay/voice_ops.py:328-332`
```python
    said = _norm(transcript)
    if said in SLEEP_PHRASES:
        return {"ops": [{"op": "sleep"}], "say": "Sleeping", "skipped": []}
    if said in SHOW_PHRASES:
        return {"ops": [{"op": "show_lists"}], "say": "Your lists", "skipped": []}
```
`_norm()` (`:315`) lowercases, strips punctuation and a leading "hey" / "ok" / "aurelius" -> "Aurelius, open all lists." still matches.
prompt rule for longer sentences that still go to the model (`:73`):
```
- "show/open/go to my lists", "my list" or "all lists" with no specific list named means show_lists. Naming one list means switch.
```
Pico side (`firmware/app.py:39-45`):
```python
        if voicecmd.show_picker:            # "open my lists"
            mode = "picker"
            psel = lists.names().index(lists.current_name())
            display.draw_picker(psel)
            if say != "Your lists":         # other changes too -> show what happened
                display.toast(say)
            return
```

## 6. sleep by voice

same fast path, `SLEEP_PHRASES` (`relay/voice_ops.py:302`): sleep / go to sleep / sleep now / goodnight / good night / night night / go to bed / lights out / turn off / power down. combined sentences ("add milk and go to sleep") go through DeepSeek, which returns `add` + `sleep`.
Pico (`firmware/app.py:35-38`):
```python
        if voicecmd.go_sleep:               # "sleep" / "goodnight"
            display.saver()
            asleep = True
            return
```
no LED blink on sleep (`firmware/voicecmd.py:78-79`, `if ok and not go_sleep:`). wake = any press, same as idle sleep.

## 7. V5 design catch — stray button events after a voice command

**problem.** the voice hold lasts several seconds (record + upload + STT + AI) and `btn.poll()` isn't running the whole time. whatever the button handler sees afterwards (release edges, a hold that looks like ACTION_LONG) could land on `list_view` as a check-off or a delete nobody asked for.

**fix.** after every voice command: wait until all three buttons are up, then throw away 200 ms of polled events.

`firmware/app.py:85-93`
```python
def _settle(btn):
    # after a voice command: wait for all buttons up, then discard anything
    # the button handler queued during the long hold (no stray check/delete)
    while any(p.value() == 0 for p in _pins):
        time.sleep_ms(10)
    t0 = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), t0) < 200:
        btn.poll()
        time.sleep_ms(10)
```
`_pins = [Pin(2), Pin(3), Pin(4)]` — `Pin(n)` with no mode = read the existing pin without reconfiguring it, so `buttons.py` keeps ownership (same in `voicecmd.py`).
test 8 of the V5 table (command, then tap DOWN -> nothing checked or deleted) passes.

## 8. V5 error handling on the device

`firmware/voicecmd.py:54-65` — every failure ends as a one-line banner instead of a crash:

| situation | banner |
| --- | --- |
| released before 0.4 s of audio (`MIN_BYTES`, `:7`) | `Too short - hold and talk` |
| hotspot off / can't join in 10 s | `No Wi-Fi` |
| relay not running / Mac off the hotspot | `Can't reach relay` |
| relay returned non-200 (`net.py:65` raises `ValueError`) | `Relay error` |
| DeepSeek call failed | `AI error` (relay side, full error in the reply's `error` field) |
| nothing understood | `Didn't catch that` / model's note |

Wi-Fi joins in the background at boot (`firmware/app.py:99`, `net.start()`), so a command doesn't wait on the join. if the boot join failed (hotspot was off), `net.wifi()` retries (`firmware/net.py:25`, only calls `connect()` again when not already `STAT_CONNECTING`). upload timeout 15 s.

## 9. workflow snags (no code change)

- **pip into the wrong Python.** the relay has its own venv: `source .venv/bin/activate` first (prompt shows `(.venv)`), then `pip install`. new Terminal window = activate again.
- **`.env` didn't get written.** `echo 'DEEPSEEK_API_KEY=...'` without `> .env` only prints. `cat .env` to check. `.env` is gitignored.
- **commands pasted into the running relay window did nothing.** uvicorn owns that Terminal while it runs. Ctrl+C, wait for `%`, then run. `# ...` lines in instructions are notes, not commands.
- **`ls: /Users/.../Downloads: Operation not permitted`.** macOS privacy blocks Terminal from Downloads (and the files had never been downloaded). files went straight into `~/aurelius-relay` instead. permanent alt: System Settings -> Privacy & Security -> Files and Folders -> Terminal -> Downloads.
- **after replug, stuck on the plaque.** UP was held while plugging in = escape hatch (`firmware/main.py:6`, `if Pin(2, Pin.IN, Pin.PULL_UP).value() == 0:`) -> app skipped; e-ink keeps the last image with no power, so it looked frozen. replug without touching anything. onboard LED x3 = app was skipped.

## V5 test table (all pass)

| # | do | expect |
| --- | --- | --- |
| 1 | "add batteries" | item appears, `Added Batteries`, 1 blink |
| 2 | "check off batteries" | struck through, `Done: Batteries` |
| 3 | "add bread and milk to groceries" | `Added 2 items`, both on Groceries |
| 4 | "make a camping list with tent and lantern" | switches to Camping, 2 items |
| 5 | "what's the weather" | `Not a list command`, nothing changes |
| 6 | let go as the LED starts | `Too short - hold and talk` |
| 7 | relay stopped | `Can't reach relay` |
| 8 | relay back, command, then tap DOWN | banner clears, no stray check/delete |
| 9 | standalone (Thonny closed) | same as 1 |
| 10 | "open my list" / "go to my lists" | picker opens, AI 0.0 s |
| 11 | "show me groceries" | Groceries directly, not the picker |
| 12 | "sleep" / "Aurelius, goodnight" | plaque, no blink, AI 0.0 s; any press wakes |
