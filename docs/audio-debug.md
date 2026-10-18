# Getting clean audio out of the mic (Oct 18)

The mic passed `mictest.py` right after soldering: the bars jumped when I talked and spiked when I clapped. So I assumed audio was done and moved on to voice mode. The first step there was recording a clip to the Pico. That turned into most of the afternoon, because there were four separate problems stacked on top of each other, and each one hid the next. This is the whole chain, in order.

---

## 1. The recording froze and Stop couldn't kill it

**What happened.** The first `voice.py` recorded straight to a file on flash, using `rectest.py`. I held UP+ACTION and the LED started pulsing. I spoke and let go, and nothing printed. Thonny's Stop button didn't work either: the Pico showed as busy and I couldn't save files to it. (Thonny also printed some red `SyntaxWarning: 'return' in a 'finally' block` lines. Those come from Thonny's own code running on Python 3.14, not from the Pico, so I ignored them.)

**Getting back in.** I unplugged it, held UP while plugging it back in (the escape hatch built into `main.py`), and then clicked Stop. That got me a working prompt again.

**Finding where it hung.** The first test only printed at the very end, so I couldn't tell where it was stuck. I rewrote `rectest.py` to print a numbered line at each stage. It got to `3. LED pulsing: speak now` and stopped there, even after I let go of the buttons. So it was hanging inside the recording loop.

**Why.** Stop couldn't interrupt it, which meant the code was stuck inside a low-level call, not in a normal Python loop. The likely one was `mic.readinto()` waiting for audio that never arrived. The difference from `mictest` was that the recording loop wrote to flash every 32 ms. On the Pico, a flash write briefly pauses interrupts, and the I2S mic stream depends on interrupts to keep its buffers moving. A pause at the wrong moment can stall the stream for good, and then `readinto()` waits forever.

- Before the real fix, I first set the I2S buffer back from 40000 to 20000, the value that already worked in `mictest`. Pasting that one-line edit broke the line (`SyntaxError` on line 31), so I replaced the whole file instead. The buffer size turned out not to be the cause, but it removed one variable.

**Fix.** Record into RAM, not flash. `voice.py` now allocates a 192 KB buffer once, at import (6 s × 16,000 samples × 2 bytes). Recording fills that buffer, and the file only gets written after the mic is turned off.

- Free RAM went from 451,536 to 239,632 bytes after the buffer, which leaves plenty of room.
- This is also better for voice mode: the clip can upload straight from memory without wearing out the flash.

## 2. The test crashed with MemoryError right after recording

**What happened.** The recording now worked: it reached `4. released` and saved `rec.pcm`. Then it crashed with `MemoryError: memory allocation failed, allocating 160768 bytes`.

**Why.** To find the loudest sample, the test did `array.array("h", voice.BUF[:nbytes])`. Slicing a bytearray makes a full copy, here 160 KB, and there wasn't a free block that big left.

**Fix.** I added `voice.peak()`, a viper function that scans the buffer in place without copying it. `ptr16` reads the values as unsigned, so anything over 32767 gets 65536 subtracted to make it signed again.

## 3. The timing was right, but the peak was 32768

**Result.**
```
recorded 3.30 s of audio in 3.33 s wall time
saved rec.pcm, 105472 bytes
peak 32768 (of 32767)
```
- 3.30 s of audio in 3.33 s of real time means no audio was dropped, so the RAM approach works.
- A peak of 32768 means a sample hit the bottom clipping limit. My first guess was the mic's startup spike: the INMP441 needs about 85 ms to settle once its clock starts, and the code only threw away 32 ms. So I changed it to skip about 200 ms (6 reads).

**Actually listening.** Numbers can look fine while the sound is wrong, so I wrote `relay/pcm2wav.py` to wrap the raw file in a WAV header. I copied `rec.pcm` to the Mac (Thonny → View → Files → Download to…) and played it with `afplay`. It was **loud static with my voice faintly underneath.** Something was very wrong.

## 4. The static: only 8 of the 24 bits were getting through

My first thought was bad soldering. But a dead joint usually gives silence or pure noise, and I could hear my voice. So I wanted to look at the raw data first.

### Test 1: dump raw words in a quiet room (`snippets/rawdump_v1.py`)
```
fe000000 -512
ff000000 -256
00000000 0
...
low byte nonzero in 0/512 words
quiet: mean -178, min -1024, max 0
```
**What it told me.** Every word had data only in its **top 8 bits**, and the lower 24 were always zero. In effect the mic was being read as an 8-bit device. In a quiet room the value jumped between big steps (0, -256, -512 in top-16-bit terms). That coarse rounding is the static. Normal speech only moved the value about one step, which is why my voice was so faint.

### Test 2: three clock speeds, both channels (`snippets/rawdump_v2.py`)
I wanted to rule out the clock speed and check which I2S slot the mic actually uses.
```
16000 L  low bits used in  18/512   e.g. fe000000 ff800000 ff800000 00000000
16000 R  low bits used in 512/512   e.g. ffffffff ffffffff ffffffff ffffffff
32000 L  low bits used in  40/512   ...
48000 L  low bits used in  57/512   ...
(R = ffffffff at every rate)
```
**What it told me.**
- The clock speed made no difference, so that wasn't the cause.
- R, the slot where the mic should be silent, read as **all 1s**.
- In binary, every L word was a **run of 1s followed by only 0s**: `ff800000` is nine 1s then zeros, `fe000000` is seven, `fc000000` is six. The line could fall from high to low partway through a word but never came back up.

That matched a known **RP2350 chip quirk (erratum E9)**. When a pin's internal pull-down is on and the device driving it lets go, the pin can get stuck around 2 V and read as 1. The INMP441 lets go of SD for part of every frame, so it's exactly the kind of device this affects.

### Test 3: turn the pull-down on GP18 off and compare (`snippets/rawdump.py`)
```
A: as is        pad18=056
   L low bits used in  23/512   e.g. 00000000 ...
   R low bits used in 512/512   e.g. ffffffff ...
B: no pulldown  pad18=052
   L low bits used in  31/512   e.g. 00000000 ... 18000000
   R low bits used in  10/512   e.g. 00000000 ...
```
(`pad18` is the GPIO18 pad register. 0x056 → 0x052 is bit 2, the pull-down, being switched off.)

**What it told me.** With the pull-down off, R went quiet, so E9 was real and explained the all-1s R slot. But **L was still almost empty**, and L is where the mic's audio should be. So the mic's data wasn't reaching GP18 properly. The "runs of 1s" were the pin glitch layered on top of a line that was barely being driven. **That made it a hardware problem.** It also explained why `mictest` had looked OK: it only measured loudness from the top bits, which is all that was getting through.

## 5. The actual fix: rewire and resolder

I pulled the mic and all six jumpers and rebuilt it from scratch, mapping every pin to an exact hole instead of placing things loosely:

| Row | Left of gap | Right of gap |
| --- | --- | --- |
| 46 | SD | SCK |
| 47 | VDD | WS |
| 48 | GND | L/R |

| Pin | From | To |
| --- | --- | --- |
| SCK | j46 | j20 (GP16) |
| WS | j47 | j19 (GP17) |
| L/R | j48 | right − rail |
| SD | a46 | j17 (GP18) |
| VDD | a47 | left + rail |
| GND | a48 | left − rail |

I also reflowed the solder joints, since some of them weren't full shiny cones.

**Result (`snippets/rawdump.py` again).**
```
A: as is        L low bits used in 512/512   e.g. 0130ca00 0127a3ff 012b5e00 012cbbff
B: no pulldown  L low bits used in 512/512   e.g. 005fddff 005c0c00 0058aa00 005c0000
```
All 512 words carried real, varied 24-bit data. I recorded again with `rectest.py`, converted it, played it on the Mac, and **it was clear as day.**

The pull-down change (`mem32` on the pad register) isn't in `voice.py`. Mono mode only reads L, and L is fully driven by the mic, so the glitch on the silent R slot doesn't matter for recording.

---

## What I took from it
- **Passing one test isn't proof.** `mictest` only measured loudness, so a mic delivering 8 of its 24 bits still looked fine. A test should check what the next stage actually needs. In this case that meant listening to the audio.
- **Dump the raw data.** One screen of hex words found the problem faster than any amount of guessing. A run of 1s followed by all 0s, in every word, is a pattern I'll recognize next time.
- **Change one thing at a time, and print each stage.** The numbered prints showed exactly where the recording hung. The A/B pull-down test separated a chip quirk from a wiring fault.
- **Don't write to flash while I2S is streaming.** Record to RAM, and write the file afterwards.
- **Watch for big hidden copies in MicroPython.** Slicing a large buffer makes a full copy, so scan buffers in place with viper.
- **Joints and breadboard contacts can fail partially.** A marginal SD connection still lets some signal through, enough to fool a quick check but nowhere near enough for clean audio. When a signal looks almost right, suspect the contact.
- **Keep `snippets/rawdump.py`.** It's a 5-second mic health check. A healthy mic shows L "low bits used" at about 512/512.
