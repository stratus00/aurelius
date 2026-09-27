# hello.py — P3 done-check. Draw from a custom script, then unplug: text stays (e-ink).
from epd_2in9 import EPD_2in9_Landscape

epd = EPD_2in9_Landscape()
epd.Clear(0xff)
epd.fill(0xff)
epd.text("AURELIUS", 10, 10, 0x00)
epd.hline(10, 22, 276, 0x00)
epd.text("UU002 - Unumusu Laboratory", 10, 32, 0x00)
epd.display(epd.buffer)
epd.sleep()
