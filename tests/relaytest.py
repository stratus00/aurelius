# relaytest.py — P7 part D. Pico -> relay /health over the hotspot.
# done = 200 {"status":"ok","relay":"Aurelius"} here + GET /health in relay Terminal.
import network, time, config, requests
wlan = network.WLAN(network.STA_IF); wlan.active(True)
if not wlan.isconnected():
    wlan.connect(config.WIFI_SSID, config.WIFI_PASS)
    while not wlan.isconnected(): time.sleep(0.5)
r = requests.get(config.RELAY_URL + "/health")
print(r.status_code, r.text); r.close()
