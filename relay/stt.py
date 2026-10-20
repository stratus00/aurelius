# stt.py — local speech-to-text (V3)
# reads the 16 kHz mono WAV directly (skips PyAV, whose version clashes with faster-whisper)
import sys, time, wave
import numpy as np
from faster_whisper import WhisperModel

MODEL = "base.en"        # try "small.en" if accuracy is poor (slower)
_model = None

def model():
    global _model
    if _model is None:
        _model = WhisperModel(MODEL, device="cpu", compute_type="int8")
    return _model

def load_wav(path):
    with wave.open(str(path), "rb") as w:
        pcm = w.readframes(w.getnframes())
    return np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768.0

def transcribe(path):
    segs, _ = model().transcribe(load_wav(path), language="en", beam_size=1)
    return " ".join(s.text.strip() for s in segs).strip()

if __name__ == "__main__":
    t0 = time.time(); model()
    print(f"model loaded in {time.time() - t0:.1f} s")
    for p in sys.argv[1:]:
        t0 = time.time()
        txt = transcribe(p)
        print(f"{time.time() - t0:.1f} s  {p}: {txt}")
