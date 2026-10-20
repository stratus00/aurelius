"""test_ops.py - exercise voice_ops without the Pico.

  python3 test_ops.py                 run the live suite against DeepSeek
  python3 test_ops.py "add milk"      one live transcript
  python3 test_ops.py --offline       validation tests only (no API calls)
"""
import json
import sys
import time

import voice_ops as vo

STATE = {
    "current": "To-do",
    "lists": {
        "To-do": [
            {"text": "Call dentist", "done": False},
            {"text": "Email professor", "done": False},
            {"text": "Laundry", "done": True},
        ],
        "Groceries": [
            {"text": "Milk", "done": False},
            {"text": "Eggs", "done": True},
            {"text": "Greek yogurt", "done": False},
        ],
        "Lab": [
            {"text": "Order flux pen", "done": False},
        ],
    },
}

LIVE = [
    "add bread to groceries",
    "add bread, butter, and orange juice to the grocery list",
    "um I called the dentist",
    "check off milk and yogurt",
    "remove laundry",
    "clear the done stuff on groceries",
    "make a new list called camping and put tent and sleeping bag on it",
    "switch to lab",
    "rename lab to workbench",
    "add eggs to groceries",                 # eggs is done -> should become uncheck
    "check off the flux pen",                # item on a non-current list
    "delete the laundry list",               # no such list
    "what time is it",                       # not a list command
    "at mail professor",                     # STT error for "email professor"?
    "open my lists",
    "go to my lists",
    "show me the groceries list",            # names a list -> switch, not show_lists
    "add milk and then show my lists",
    "add milk and then go to sleep",         # combined: goes through the AI
]

# (name, fake model reply, expected op kinds after validation)
OFFLINE = [
    ("plain add", {"ops": [{"op": "add", "list": "Groceries", "text": "bread"}]}, ["add"]),
    ("fuzzy list", {"ops": [{"op": "add", "list": "grocery", "text": "Bread"}]}, ["add"]),
    ("fuzzy item", {"ops": [{"op": "check", "item": "call the dentist"}]}, ["check"]),
    ("missing item", {"ops": [{"op": "delete", "item": "Skydiving"}]}, []),
    ("dup add", {"ops": [{"op": "add", "list": "Groceries", "text": "Milk"}]}, []),
    ("re-add done", {"ops": [{"op": "add", "list": "Groceries", "text": "eggs"}]}, ["uncheck"]),
    ("new then use", {"ops": [{"op": "new_list", "name": "camping"},
                              {"op": "add", "list": "Camping", "text": "Tent"},
                              {"op": "switch", "name": "Camping"}]}, ["new_list", "add", "switch"]),
    ("new existing", {"ops": [{"op": "new_list", "name": "groceries"}]}, ["switch"]),
    ("rename", {"ops": [{"op": "rename_list", "name": "Lab", "new": "workbench"}]}, ["rename_list"]),
    ("bad op", {"ops": [{"op": "launch_rocket"}]}, []),
    ("garbage", "not a dict", []),
    ("unicode", {"ops": [{"op": "add", "text": "Cr\u00e8me br\u00fbl\u00e9e \u2014 caf\u00e9"}]}, ["add"]),
    ("show lists", {"ops": [{"op": "show_lists"}]}, ["show_lists"]),
    ("add + show", {"ops": [{"op": "add", "list": "Groceries", "text": "Bread"},
                            {"op": "show_lists"}]}, ["add", "show_lists"]),
    ("add + sleep", {"ops": [{"op": "add", "text": "Milk2"}, {"op": "sleep"}]}, ["add", "sleep"]),
    ("note only", {"ops": [], "note": "Not a list command"}, []),
]


def show(res):
    for o in res["ops"]:
        print("   ", json.dumps(o))
    if res.get("skipped"):
        print("    skipped:", res["skipped"])
    if res.get("error"):
        print("    ERROR:", res["error"])
    print("    screen: [" + res["say"] + "]")


FAST = ["Sleep.", "Go to sleep.", "Aurelius, sleep.", "Goodnight!", "Hey Aurelius, go to bed."]


def offline():
    bad = 0
    for t in FAST:                                  # no API call: fast path
        res = vo.transcript_to_ops(t, STATE)
        ok = [o["op"] for o in res["ops"]] == ["sleep"]
        bad += not ok
        print(("PASS " if ok else "FAIL ") + "fast sleep: " + t)
    for t in ["Open my list.", "Show my lists!", "Go to my lists.", "Aurelius, open all lists."]:
        res = vo.transcript_to_ops(t, STATE)
        ok = [o["op"] for o in res["ops"]] == ["show_lists"]
        bad += not ok
        print(("PASS " if ok else "FAIL ") + "fast show: " + t)
    for name, raw, want in OFFLINE:
        res = vo.validate(raw, STATE)
        got = [o["op"] for o in res["ops"]]
        ok = got == want and len(res["say"]) <= vo.SAY_MAX
        bad += not ok
        print(("PASS " if ok else "FAIL ") + name)
        show(res)
    print("\n" + ("all passed" if not bad else str(bad) + " failed"))
    return bad


def live(transcripts):
    print("model:", vo.MODEL)
    for t in transcripts:
        t0 = time.time()
        res = vo.transcript_to_ops(t, STATE)
        print("\n> " + t + "   (" + format(time.time() - t0, ".1f") + " s)")
        show(res)


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["--offline"]:
        sys.exit(1 if offline() else 0)
    live([" ".join(args)] if args else LIVE)
