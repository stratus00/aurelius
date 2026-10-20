import json, time, wave
from pathlib import Path
from fastapi import FastAPI, Request

app = FastAPI()
CLIPS = Path(__file__).with_name("clips")
CLIPS.mkdir(exist_ok=True)

@app.get("/health")
def health():
    return {"status": "ok", "relay": "Aurelius"}

@app.post("/voice")
async def voice(request: Request):
    # body = list state JSON (X-State-Len bytes), then raw 16-bit 16 kHz mono PCM
    body = await request.body()
    n = int(request.headers.get("x-state-len", "0"))
    state = json.loads(body[:n] or b"{}")
    pcm = body[n:]
    path = CLIPS / time.strftime("%Y%m%d-%H%M%S.wav")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000)
        w.writeframes(pcm)
    secs = len(pcm) / 32000
    print(f"[voice] {secs:.2f} s -> {path.name}, {len(state.get('lists', {}))} lists")
    return {"ops": [], "say": f"Got {secs:.1f} s", "file": path.name}
