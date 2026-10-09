# wifiscan.py — P7. List every network name the Pico can hear. Ran in Shell.
# used to debug status -2: hotspot only showed up once the Personal Hotspot screen was open.
import network; w = network.WLAN(network.STA_IF); w.active(True); [print(n[0]) for n in w.scan()]
