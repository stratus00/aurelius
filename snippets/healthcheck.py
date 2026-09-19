# healthcheck.py — P1. Board / clock / free RAM / free flash. Ran in Shell.
# expect: "Pico 2 W with RP2350", ~150 MHz, few hundred KB RAM, few MB flash
import os, gc, machine
print(os.uname().machine)
print(machine.freq() // 1_000_000, "MHz")
gc.collect(); print(gc.mem_free() // 1024, "KB RAM free")
s = os.statvfs('/'); print(s[0] * s[3] // 1024, "KB flash free")
