# displaytest.py — draws a test list and scrolls through it
# builds a "Test" list (10 items, 1 long, 2 checked) — doesn't touch Groceries.
# expect: full refresh, header "Test  2/10", 7 rows, Eggs highlighted, dentist item cut w/ "..",
# filled box + strike on Lab report / Pick up package, scrollbar; highlight steps down w/ partials,
# scrolls past row 7; "done" in Shell.
import time, lists, display

lists.load()
if lists.new_list("Test"):
    for t in ["Eggs", "Call the dentist about the appointment on Tuesday",
              "Lab report", "Laundry", "Pick up package", "Read chapter 4",
              "Email professor", "Buy batteries", "Charge phone", "Water plants"]:
        lists.add(t, "Test")
    lists.set_done(2, True, "Test")
    lists.set_done(4, True, "Test")
lists.switch("Test")

display.draw_list(0, full=True)
time.sleep(2)
for i in range(1, len(lists.items())):
    display.draw_list(i)
    time.sleep(0.5)
display.sleep()
print("done")
