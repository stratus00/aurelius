# wifitest.py — P7 part B. Join the hotspot from config.py.
# status -2 = network not found (5 GHz / hotspot not broadcasting / name typo). -3 = wrong password.
import network, time, config
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(config.WIFI_SSID, config.WIFI_PASS)
for i in range(20):
    if wlan.isconnected(): break
    print("connecting...", wlan.status()); time.sleep(1)
print("Connected! IP:", wlan.ifconfig()[0]) if wlan.isconnected() else print("Failed, status:", wlan.status())
