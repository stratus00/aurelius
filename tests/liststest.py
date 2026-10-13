# liststest.py — wipes lists and runs a fresh check
# expect:
#   Fresh start: ['To-do'] | current: To-do
#   Lists: ['Groceries', 'To-do'] | current: Groceries
#   0 [ ] Eggs
#   1 [x] Milk
# then power-cycle and DON'T rerun this (it wipes). instead in Shell:
#   import lists; lists.load(); print(lists.data)
import os, lists
for f in ("lists.json", "lists.tmp"):
    try: os.remove(f)
    except OSError: pass

lists.load()
print("Fresh start:", lists.names(), "| current:", lists.current_name())

lists.new_list("Groceries")
lists.switch("Groceries")
lists.add("Eggs"); lists.add("Milk"); lists.add("Rice")
lists.toggle(1)    # check off Milk
lists.delete(2)    # delete Rice

print("Lists:", lists.names(), "| current:", lists.current_name())
for i, it in enumerate(lists.items()):
    print(i, "[x]" if it["done"] else "[ ]", it["text"])
