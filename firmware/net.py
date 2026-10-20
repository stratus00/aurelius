# net.py — wifi + raw-socket upload to the relay.
# raw socket so the 192 KB audio buffer is sent straight from RAM, never copied.
import network, socket, time, json, config

def wifi(timeout_ms=15000):
    w = network.WLAN(network.STA_IF)
    w.active(True)
    try:
        w.config(pm=network.WLAN.PM_NONE)    # power-save off = faster uploads
    except Exception:
        pass
    if not w.isconnected():
        w.connect(config.WIFI_SSID, config.WIFI_PASS)
        t0 = time.ticks_ms()
        while not w.isconnected():
            if time.ticks_diff(time.ticks_ms(), t0) > timeout_ms:
                raise OSError("no wifi")
            time.sleep_ms(200)
    return w

def _hostport(url):
    hp = url.split("//", 1)[1].split("/", 1)[0]
    h, p = (hp.split(":") + ["80"])[:2]
    return h, int(p)

def post_voice(state, pcm, timeout_s=30):
    st = json.dumps(state).encode()
    host, port = _hostport(config.RELAY_URL)
    s = socket.socket()
    s.settimeout(timeout_s)
    try:
        s.connect(socket.getaddrinfo(host, port)[0][-1])
        head = ("POST /voice HTTP/1.0\r\nHost: %s\r\n"
                "Content-Type: application/octet-stream\r\n"
                "Content-Length: %d\r\nX-State-Len: %d\r\n\r\n") % (host, len(st) + len(pcm), len(st))
        s.sendall(head.encode())
        s.sendall(st)
        mv = memoryview(pcm)
        for i in range(0, len(mv), 4096):
            s.sendall(mv[i:i + 4096])
        resp = b""
        while True:
            chunk = s.recv(512)
            if not chunk:
                break
            resp += chunk
    finally:
        s.close()
    head, _, body = resp.partition(b"\r\n\r\n")
    code = int(head.split(b" ")[1].decode())
    if code != 200:
        raise OSError("relay %d" % code)
    return json.loads(body.decode())
