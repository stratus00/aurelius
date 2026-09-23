# wiring (breadboard)

rows 1-63 top->bottom, cols a-j left->right. rails: red + / blue -, both edges.
UNPLUG USB before every wiring change.

## P2 — Pico + rails
- Pico straddles gap, USB up: left pins c1-c20, right pins h1-h20.
- pin 1 (GP0) = c1, pin 20 = c20, pin 21 = h20, pin 40 = h1. right side: phys pin = 41 - row.
- j5 (row 5 = pin 36, 3V3 OUT) -> right + rail
- j3 (row 3 = pin 38, GND) -> right - rail
- bottom: right + -> left +, right - -> left - (bridge). split rails? jump the mid gap on all 4.
- right rows 1-2 = VBUS / VSYS (5 V). stay off.
- check: snippets/railtest.py (a1 -> left + reads 1, a1 -> left - reads 0).
