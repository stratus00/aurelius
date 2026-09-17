# pin map

physical pins: pin 1 top-left (USB up), down left side to 20, up right side 21-40.
no two parts share a signal pin.

| part | part pin | Pico pin | phys | notes |
| --- | --- | --- | --- | --- |
| e-ink | VCC | 3V3(OUT) | 36 | 3.3 V ONLY |
| e-ink | GND | GND | 38 | |
| e-ink | DIN | GP11 | 15 | SPI1 MOSI |
| e-ink | CLK | GP10 | 14 | SPI1 clock |
| e-ink | CS | GP9 | 12 | chip select |
| e-ink | DC | GP8 | 11 | data/command |
| e-ink | RST | GP12 | 16 | reset |
| e-ink | BUSY | GP13 | 17 | "wait" line |
| btn UP | one leg | GP2 | 4 | other leg GND |
| btn DOWN | one leg | GP3 | 5 | other leg GND |
| btn ACTION | one leg | GP4 | 6 | other leg GND |
| LED | anode via 220 ohm | GP15 | 20 | cathode GND |
| mic | VDD | 3V3(OUT) | 36 | 3.3 V, NEVER 5 V |
| mic | GND | GND | 23 | |
| mic | SCK | GP16 | 21 | I2S bit clock |
| mic | WS | GP17 | 22 | must = SCK+1 in MicroPython |
| mic | SD | GP18 | 24 | I2S data |
| mic | L/R | GND | - | left channel. floating = silence |
| batt (later) | + via switch + diode | VSYS | 39 | 1.8-5.5 V |

- display pins = Waveshare Pico driver defaults -> driver works unedited (except the BUSY timeout patch).
- NEVER power anything from pin 40 (VBUS) or 39 (VSYS) on the breadboard — 5 V.
