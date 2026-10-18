# pcm2wav.py — raw 16 kHz 16-bit mono PCM -> .wav
import sys, wave
src = sys.argv[1] if len(sys.argv) > 1 else "rec.pcm"
with open(src, "rb") as f:
    data = f.read()
with wave.open(src.rsplit(".", 1)[0] + ".wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000)
    w.writeframes(data)
print("wrote", src.rsplit(".", 1)[0] + ".wav", len(data) // 32000, "s")
