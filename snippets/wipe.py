# wipe.py — P1. Delete EVERY file + folder on the Pico (MicroPython stays).
# Used to clear the v0 build (old main.py, epaper29.py, Pico_ePaper_2in9.py).
# Ran in Shell. Prints [] when clean.
import os
def wipe(path='/'):
    for name in os.listdir(path):
        full = path.rstrip('/') + '/' + name
        if os.stat(full)[0] & 0x4000:   # it's a folder
            wipe(full); os.rmdir(full)
        else:
            os.remove(full)
wipe()
print(os.listdir())
