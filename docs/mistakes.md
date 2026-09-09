# mistakes

symptom -> cause -> fix. v0 = first attempt (shelved). numbers = restart.

| # | phase | symptom | cause | fix / lesson |
| --- | --- | --- | --- | --- |
| v0-1 | v0 buttons | buttons stuck / wrong reads | not bridging the center gap -> legs shorted on one side | straddle gap e<->f, signal e side, GND f side. lesson: exact coords, not vague placement |
| v0-2 | v0 display | init hangs on "e-Paper busy" forever | suspected driver PULL_UP on BUSY; never solved in v0 | real cause found in restart (#7): display boots stuck busy, needs RST pulse. + no timeout in ReadBusy = frozen Pico (#8) |
| v0-3 | v0 display | lots of guessing on hat/socket pin mapping | socket is a mirror image of the Pico seen from behind | restart: use the 8-pin cable connector, no mirror mapping |
