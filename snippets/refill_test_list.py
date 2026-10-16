# refill_test_list.py — refill the Test list after deleting everything in the check/delete test.
# one line, pasted at the >>> prompt with apptest stopped. adds 8 items to the CURRENT list.
import lists; lists.load(); [lists.add(t) for t in ["Eggs", "Lab report", "Laundry", "Read chapter 4", "Email professor", "Buy batteries", "Charge phone", "Water plants"]]

# reset the whole Test list instead:
#   import lists; lists.load(); lists.delete_list("Test")   then rerun displaytest.py
