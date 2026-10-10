# relay

Runs on the Mac. Lives at `~/aurelius-relay` on the laptop (this folder = copy of it).
Now: `/health` only. Later: `/voice` (audio + lists.json in -> list ops JSON out).

## first-time setup
```bash
python3 --version            # accept dev-tools install if asked
mkdir ~/aurelius-relay && cd ~/aurelius-relay
python3 -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn   # or: pip install -r requirements.txt
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

stop: Ctrl+C in relay window.

## snags
- Pico + Mac on diff networks
- Mac firewall blocking 8000
- Mac IP changed after reconnect -> redo step 5/6
