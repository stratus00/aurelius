"""voice_ops.py - transcript -> validated list operations (Aurelius voice V4).

Pipeline:  transcript + list state  ->  DeepSeek (JSON mode)  ->  validate()  ->  {"ops", "say"}

- State is the Pico's lists.json dict: {"current": str, "lists": {name: [{"text", "done"}]}}
- validate() replays every op on a copy of the state, so the Pico only ever
  receives ops that will succeed, with exact list/item names already resolved.
- "say" is built here (not by the model) so the confirm line always matches
  what actually happened and always fits the screen.
"""
import copy
import difflib
import json
import os
import unicodedata
from pathlib import Path

# ---------- config ----------
def _load_env():
    """Minimal .env loader (KEY=VALUE lines) so no extra package is needed."""
    p = Path(__file__).with_name(".env")
    if not p.exists():
        return
    for line in p.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

_load_env()

MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-flash")
SAY_MAX = 36        # 296 px wide / 8 px font = 37 chars, keep 1 spare
ITEM_MAX = 40       # longest item text accepted
NAME_MAX = 20       # longest list name accepted (picker screen)
MAX_OPS = 10        # cap per command

_client = None

def client():
    global _client
    if _client is None:
        key = os.environ.get("DEEPSEEK_API_KEY")
        if not key:
            raise RuntimeError("DEEPSEEK_API_KEY not set (put it in .env next to this file)")
        from openai import OpenAI   # imported here so offline tests need no package
        _client = OpenAI(api_key=key, base_url="https://api.deepseek.com", timeout=20)
    return _client


# ---------- prompt ----------
SYSTEM = """You turn a spoken command into edits for a small to-do list device.
Reply with JSON only, in this shape: {"ops": [...], "note": ""}

Operations:
{"op":"add","list":L,"text":T}        add item T
{"op":"check","list":L,"item":I}      mark item done
{"op":"uncheck","list":L,"item":I}    mark item not done
{"op":"delete","list":L,"item":I}     remove item
{"op":"clear_done","list":L}          remove every done item
{"op":"new_list","name":N}            create a list
{"op":"switch","name":N}              show list N on screen
{"op":"rename_list","name":N,"new":M}
{"op":"delete_list","name":N}

Rules:
- L, I and N must be copied exactly from STATE. Leave out "list" to mean the current list.
- A list created earlier in the same command can be used by later ops.
- T is short, written the way someone writes on a list: first letter capitalized, no filler words.
- Several items in one sentence means one op per item.
- The transcript comes from speech recognition and may contain mistakes. When the intent is clear, use the closest match in STATE.
- Never invent items to check, uncheck or delete.
- If the command is unclear, not about the lists, or names something not in STATE, return {"ops": [], "note": "<why, under 30 characters>"}.

Example
STATE: {"current":"To-do","lists":{"To-do":[{"text":"Call dentist","done":false}],"Groceries":[{"text":"Milk","done":false},{"text":"Eggs","done":true}]}}
TRANSCRIPT: add bread and butter to groceries and I already called the dentist
JSON: {"ops":[{"op":"add","list":"Groceries","text":"Bread"},{"op":"add","list":"Groceries","text":"Butter"},{"op":"check","item":"Call dentist"}],"note":""}

Example
STATE: (same as above)
TRANSCRIPT: start a camping list with tent and headlamp
JSON: {"ops":[{"op":"new_list","name":"Camping"},{"op":"add","list":"Camping","text":"Tent"},{"op":"add","list":"Camping","text":"Headlamp"},{"op":"switch","name":"Camping"}],"note":""}

Example
STATE: (same as above)
TRANSCRIPT: what's the weather tomorrow
JSON: {"ops":[],"note":"Not a list command"}
"""


def ask_model(transcript, state):
    """Raw model reply as a dict. Retries once (JSON mode can return empty content)."""
    msgs = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": "STATE: " + json.dumps(state) + "\nTRANSCRIPT: " + transcript + "\nJSON:"},
    ]
    last_err = None
    for _ in range(2):
        r = client().chat.completions.create(
            model=MODEL,
            messages=msgs,
            response_format={"type": "json_object"},
            temperature=0,
            max_tokens=500,
        )
        content = (r.choices[0].message.content or "").strip()
        if not content:
            last_err = "empty reply"
            continue
        try:
            return json.loads(content)
        except ValueError:
            last_err = "bad JSON: " + content[:80]
    raise ValueError("model gave no usable JSON (" + str(last_err) + ")")


# ---------- validation ----------
def _ascii(s):
    """Pico's framebuf font is ASCII only: fold accents, drop anything else."""
    s = unicodedata.normalize("NFKD", str(s))
    s = s.replace("\u2019", "'").replace("\u2018", "'").replace("\u201c", '"').replace("\u201d", '"')
    return " ".join(s.encode("ascii", "ignore").decode().split())


def _match(word, options, cutoff=0.6):
    """Exact (case-insensitive) match first, then closest fuzzy match, else None."""
    if not isinstance(word, str) or not word.strip():
        return None
    w = word.strip().lower()
    lower = {o.lower(): o for o in options}
    if w in lower:
        return lower[w]
    hit = difflib.get_close_matches(w, list(lower), n=1, cutoff=cutoff)
    return lower[hit[0]] if hit else None


def _short(s, n=14):
    return s if len(s) <= n else s[: n - 2] + ".."


def _check(op, s):
    """Return (clean_op, None) or (None, reason). s is the simulated state."""
    if not isinstance(op, dict):
        return None, None
    kind = op.get("op")
    lists = s["lists"]

    if kind in ("add", "check", "uncheck", "delete", "clear_done"):
        lname = s["current"] if not op.get("list") else _match(op["list"], lists)
        if lname is None:
            return None, "No list '" + _short(_ascii(op["list"])) + "'"
        items = lists[lname]

        if kind == "clear_done":
            return {"op": "clear_done", "list": lname}, None

        if kind == "add":
            text = _ascii(op.get("text", ""))[:ITEM_MAX]
            if not text:
                return None, None
            text = text[0].upper() + text[1:]
            same = next((it for it in items if it["text"].lower() == text.lower()), None)
            if same and not same["done"]:
                return None, _short(same["text"]) + " already there"
            if same and same["done"]:      # re-adding a done item = un-check it
                return {"op": "uncheck", "list": lname, "item": same["text"]}, None
            return {"op": "add", "list": lname, "text": text}, None

        # check / uncheck / delete need an existing item
        name = _match(op.get("item"), [it["text"] for it in items])
        if name is None:
            return None, "No '" + _short(_ascii(op.get("item", "?"))) + "' in " + _short(lname, 10)
        return {"op": kind, "list": lname, "item": name}, None

    if kind == "new_list":
        name = _ascii(op.get("name", ""))[:NAME_MAX]
        if not name:
            return None, None
        name = name[0].upper() + name[1:]
        existing = _match(name, lists, cutoff=1.0)
        if existing:                       # already exists = just show it
            return {"op": "switch", "name": existing}, None
        return {"op": "new_list", "name": name}, None

    if kind in ("switch", "delete_list", "rename_list"):
        name = _match(op.get("name"), lists)
        if name is None:
            return None, "No list '" + _short(_ascii(op.get("name", "?"))) + "'"
        if kind == "switch":
            return {"op": "switch", "name": name}, None
        if kind == "delete_list":
            if len(lists) == 1:
                return None, "Can't delete last list"
            return {"op": "delete_list", "name": name}, None
        new = _ascii(op.get("new", ""))[:NAME_MAX]
        if not new or _match(new, lists, cutoff=1.0):
            return None, "Bad new name"
        return {"op": "rename_list", "name": name, "new": new[0].upper() + new[1:]}, None

    return None, None                       # unknown op: drop silently


def _apply(op, s):
    """Mirror of lists.py, run on the simulated state."""
    k, L = op["op"], s["lists"]
    if k == "add":
        L[op["list"]].append({"text": op["text"], "done": False})
    elif k in ("check", "uncheck"):
        for it in L[op["list"]]:
            if it["text"] == op["item"]:
                it["done"] = (k == "check")
                break
    elif k == "delete":
        L[op["list"]] = [it for it in L[op["list"]] if it["text"] != op["item"]]
    elif k == "clear_done":
        L[op["list"]] = [it for it in L[op["list"]] if not it["done"]]
    elif k == "new_list":
        L[op["name"]] = []
    elif k == "switch":
        s["current"] = op["name"]
    elif k == "rename_list":
        L[op["new"]] = L.pop(op["name"])
        if s["current"] == op["name"]:
            s["current"] = op["new"]
    elif k == "delete_list":
        del L[op["name"]]
        if s["current"] == op["name"]:
            s["current"] = sorted(L)[0]


def _say(ops, skipped, note, final_current):
    if not ops:
        line = skipped[0] if skipped else (_ascii(note) if note else "Didn't catch that")
    elif len(ops) == 1:
        o = ops[0]
        where = "" if o.get("list") in (None, final_current) else " (" + _short(o["list"], 10) + ")"
        line = {
            "add": lambda: "Added " + _short(o["text"], 20) + where,
            "check": lambda: "Done: " + _short(o["item"], 20) + where,
            "uncheck": lambda: "Undone: " + _short(o["item"], 18) + where,
            "delete": lambda: "Removed " + _short(o["item"], 18) + where,
            "clear_done": lambda: "Cleared done" + where,
            "new_list": lambda: "New list: " + o["name"],
            "switch": lambda: "-> " + o["name"],
            "rename_list": lambda: "Renamed to " + o["new"],
            "delete_list": lambda: "Deleted list " + o["name"],
        }[o["op"]]()
    else:
        kinds = {o["op"] for o in ops if o["op"] != "switch"}
        n = sum(1 for o in ops if o["op"] != "switch")
        if kinds == {"add"}:
            line = "Added " + str(n) + " items"
        elif kinds == {"check"}:
            line = "Checked off " + str(n)
        elif kinds == {"new_list", "add"}:
            line = "New list, " + str(n - 1) + (" item" if n == 2 else " items")
        else:
            line = str(len(ops)) + " changes"
    if ops and skipped:
        line += " (" + str(len(skipped)) + " skipped)"
    return line if len(line) <= SAY_MAX else line[: SAY_MAX - 2] + ".."


def validate(raw, state):
    """Model reply -> {"ops": [...], "say": str, "skipped": [...]} (ops guaranteed to apply)."""
    s = copy.deepcopy(state)
    ops, skipped = [], []
    raw_ops = raw.get("ops") if isinstance(raw, dict) else None
    for op in (raw_ops if isinstance(raw_ops, list) else [])[:MAX_OPS]:
        clean, why = _check(op, s)
        if clean:
            _apply(clean, s)
            ops.append(clean)
        elif why:
            skipped.append(why)
    note = raw.get("note") if isinstance(raw, dict) else None
    return {"ops": ops, "say": _say(ops, skipped, note, s["current"]), "skipped": skipped}


def transcript_to_ops(transcript, state):
    """The one function the relay's /voice endpoint will call."""
    transcript = (transcript or "").strip()
    if not transcript:
        return {"ops": [], "say": "Heard nothing", "skipped": []}
    try:
        raw = ask_model(transcript, state)
    except Exception as e:
        return {"ops": [], "say": "AI error", "skipped": [], "error": str(e)}
    return validate(raw, state)
