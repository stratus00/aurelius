# config.example.py — copy to the Pico as config.py and fill in.
# real config.py is gitignored (has the hotspot password).
# hotspot: iPhone renamed to JacobsiPhone (no curly apostrophe), Maximize Compatibility ON (2.4 GHz).
WIFI_SSID = "JacobsiPhone"
WIFI_PASS = "YourPassword"
RELAY_URL = "http://172.20.10.x:8000"   # Mac IP from `ipconfig getifaddr en0`; changes per hotspot session. no trailing slash.
