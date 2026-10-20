import json, time, wave
from pathlib import Path
from fastapi import FastAPI, Request
import stt, voice_ops

app = FastAPI()
CLIPS = Path(__file__).with_name("clips")
CLIPS.mkdir(exist_ok=True)
stt.model()                      # load whisper once at startup, not on first request

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

    t0 = time.time()
    heard = stt.transcribe(path)
    t1 = time.time()
    res = voice_ops.transcript_to_ops(heard, state)
    t2 = time.time()
    res["heard"] = heard
    print(f'[voice] {len(pcm)/32000:.1f} s clip | stt {t1-t0:.1f} s: "{heard}" | ai {t2-t1:.1f} s -> {res["say"]}')
    for op in res["ops"]:
        print("   ", op)
    return res
