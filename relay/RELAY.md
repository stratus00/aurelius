# relay

Runs on the Mac. Lives at `~/aurelius-relay` on the laptop (this folder = copy of it).
`/health` + `/voice` (lists.json + PCM in -> WAV in clips/ -> faster-whisper -> DeepSeek -> validated list ops JSON out). how it works + issues: docs/voice-pipeline.md.

## first-time setup
```bash
python3 --version            # accept dev-tools install if asked
mkdir ~/aurelius-relay && cd ~/aurelius-relay
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt   # fastapi uvicorn openai faster-whisper numpy
echo 'DEEPSEEK_API_KEY=sk-...' > .env   # the > matters. .env is gitignored
cat .env                       # check it saved
```
files needed in ~/aurelius-relay: `server.py`, `stt.py`, `voice_ops.py`, `test_ops.py`.
first `python3 stt.py clips/*.wav` downloads the whisper model (~150 MB, ~45 s, once).

## test without the Pico
```bash
python3 test_ops.py --offline        # validation only, no API calls -> all passed
python3 test_ops.py                  # live suite against DeepSeek
python3 test_ops.py "add milk"       # one phrase
python3 stt.py clips/*.wav           # transcribe saved clips
```

## every session
1. iPhone: Settings -> Personal Hotspot ON, keep that screen open, Maximize Compatibility ON
2. Mac joins JacobsiPhone (same network as Pico — required)
3. start relay (stops when Terminal window closes):
```bash
cd ~/aurelius-relay
source .venv/bin/activate
uvicorn server:app --host 0.0.0.0 --port 8000
```
   macOS "allow incoming connections" -> Allow
4. browser check: http://localhost:8000/health -> `{"status":"ok","relay":"Aurelius"}`
5. 2nd Terminal: `ipconfig getifaddr en0` (blank -> try `en1`). looks like 172.20.10.x
6. put it in config.py on Pico: `RELAY_URL = "http://172.20.10.x:8000"` — re-check EVERY session, IP changes
7. Pico: run relaytest.py -> `200 {"status":"ok","relay":"Aurelius"}` + `GET /health` line in Terminal

stop: Ctrl+C in relay window. while it runs that window is busy — Ctrl+C before typing anything else, or use a 2nd window.
log per command: `[voice] 2.0 s clip | stt 0.5 s: "..." | ai 2.8 s -> <banner>` + the ops.

## snags
- Pico + Mac on diff networks
- Mac firewall blocking 8000
- Mac IP changed after reconnect -> redo step 5/6
- `TypeError: ... metadata_errors` from faster-whisper = PyAV clash; stt.py reads WAV itself so it never happens through the relay
- Terminal can't read ~/Downloads (Operation not permitted) -> move files in Finder, or allow Terminal in Privacy & Security -> Files and Folders
- banner `Can't reach relay` on the Pico = relay not running, or Mac/Pico on different networks, or stale RELAY_URL
