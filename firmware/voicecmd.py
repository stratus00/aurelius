# voicecmd.py — V5. push-to-talk -> relay -> apply list ops on the Pico.
from machine import Pin
import voice, net, lists, led

_up = Pin(2)                  # existing pins, not reconfigured (buttons.py owns them)
_act = Pin(4)
MIN_BYTES = 32000 * 4 // 10   # under 0.4 s = treat as an accidental press
show_picker = False           # command asked to open the list picker
go_sleep = False              # command asked the device to sleep

def _held():
    return _up.value() == 0 or _act.value() == 0

def _apply(op):
    global show_picker, go_sleep
    k = op.get("op")
    L = op.get("list")
    if k == "add":
        lists.add(op["text"], L)
    elif k in ("check", "uncheck", "delete"):
        i = lists.find(op["item"], L)
        if i < 0:
            return False
        if k == "delete":
            lists.delete(i, L)
        else:
            lists.set_done(i, k == "check", L)
    elif k == "clear_done":
        lists.clear_done(L)
    elif k == "new_list":
        return lists.new_list(op["name"])
    elif k == "switch":
        return lists.switch(op["name"])
    elif k == "rename_list":
        return lists.rename_list(op["name"], op["new"])
    elif k == "delete_list":
        return lists.delete_list(op["name"])
    elif k == "show_lists":
        show_picker = True
    elif k == "sleep":
        go_sleep = True
    else:
        return False
    return True

def run():
    # call while UP+ACTION is held. returns the one-line confirm for the screen.
    global show_picker, go_sleep
    show_picker = go_sleep = False
    led.pulse()
    ok = 0
    try:
        nbytes = voice.record(_held)
        if nbytes < MIN_BYTES:
            return "Too short - hold and talk"
        try:
            net.wifi()
        except OSError:
            return "No Wi-Fi"
        try:
            res = net.post_voice(lists.data, memoryview(voice.BUF)[:nbytes])
        except ValueError:
            return "Relay error"
        except OSError:
            return "Can't reach relay"
        print("heard:", res.get("heard"))
        if res.get("error"):
            print("relay error:", res["error"])
        for op in res.get("ops", []):
            try:
                if _apply(op):
                    ok += 1
            except Exception as ex:
                print("op failed:", op, ex)
        return res.get("say", "?")
    finally:
        led.off()
        if ok and not go_sleep:
            led.blink()
