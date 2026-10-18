# main.py — runs automatically on power-up.
# Hold UP while plugging in to skip the app (onboard LED blinks 3 times).
from machine import Pin
import sys, time

if Pin(2, Pin.IN, Pin.PULL_UP).value() == 0:
    onboard = Pin("LED", Pin.OUT)
    for _ in range(3):
        onboard.on(); time.sleep(0.2); onboard.off(); time.sleep(0.2)
    print("UP held at boot: app skipped")
else:
    try:
        import app
        app.run()
    except KeyboardInterrupt:
        import led
        led.off()
        print("Stopped")
    except Exception as ex:
        sys.print_exception(ex)
        try:
            with open("error.log", "a") as f:
                f.write("---\n")
                sys.print_exception(ex, f)
            import led, display
            led.flicker()
            msg = "%s: %s" % (type(ex).__name__, ex)
            lines = [msg[i:i + 36] for i in range(0, len(msg), 36)]
            display.draw_message("Error", lines + ["", "Details in error.log"])
        except Exception:
            pass
