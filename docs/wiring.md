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

## P3 — e-ink (8-pin cable, not the hat socket)
cable plugs into the top connector; M-M jumpers from cable's female tips into breadboard.

| connector | breadboard |
| --- | --- |
| VCC | right + rail |
| GND | right - rail |
| DIN | b15 (GP11) |
| CLK | b14 (GP10) |
| CS | b12 (GP9) |
| DC | b11 (GP8) |
| RST | b16 (GP12) |
| BUSY | b17 (GP13) |

- row 13 = GND pin, leave empty.
- BS jumper (back, bottom right, "SPI 4-line/3-line") must be 0. factory default.
- 3V3/VSYS jumper (back, top left): ignore, only matters when seated on the hat.

## P4 — buttons (rows 24-36, diagonal wiring)
rows 1-20 are Pico pins on both sides -> a button there would short two pins. so below.
4-leg button: legs paired. DIAGONAL corners never connected until pressed -> works any rotation.

| button | legs (cols e+f) | signal | ground |
| --- | --- | --- | --- |
| UP | rows 24 & 26 | b4 -> b24 | j26 -> right - |
| DOWN | rows 29 & 31 | b5 -> b29 | j31 -> right - |
| ACTION | rows 34 & 36 | b6 -> b34 | j36 -> right - |

signal = top row left side. ground = bottom row right side. constant "pressed" = not straddling, rotate 90.

## P5 — LED (rows 40-42)
| part | from | to |
| --- | --- | --- |
| jumper | b20 (GP15) | b40 |
| resistor 220 ohm | d40 | f40 (across gap) |
| LED long leg (+) | h40 | |
| LED short leg (-, flat rim side) | h42 | |
| jumper | j42 | right - rail |

path: GP15 -> row 40 L -> resistor -> row 40 R -> LED -> row 42 R -> GND.
never lights = LED backwards or resistor not across gap.
