# lists.py — Aurelius list storage
import json, os

FILE = "lists.json"
TMP = "lists.tmp"
data = None

def _fresh():
    return {"current": "To-do", "lists": {"To-do": []}}

def load():
    global data
    for path in (FILE, TMP):          # TMP is a backup if power died mid-save
        try:
            with open(path) as f:
                data = json.load(f)
            return data
        except (OSError, ValueError):
            pass
    data = _fresh()
    save()
    return data

def save():
    with open(TMP, "w") as f:         # write the new copy first...
        json.dump(data, f)
    try:
        os.remove(FILE)
    except OSError:
        pass
    os.rename(TMP, FILE)              # ...then swap it in

# ---- reading ----
def names():
    return sorted(data["lists"])

def current_name():
    return data["current"]

def items(name=None):
    return data["lists"][name or data["current"]]

def find(text, name=None):
    t = text.strip().lower()
    for i, it in enumerate(items(name)):
        if it["text"].lower() == t:
            return i
    return -1

# ---- items ----
def add(text, name=None):
    items(name).append({"text": text.strip(), "done": False})
    save()

def toggle(index, name=None):
    it = items(name)[index]
    it["done"] = not it["done"]
    save()

def set_done(index, done=True, name=None):
    items(name)[index]["done"] = done
    save()

def delete(index, name=None):
    items(name).pop(index)
    save()

def clear_done(name=None):
    key = name or data["current"]
    data["lists"][key] = [it for it in data["lists"][key] if not it["done"]]
    save()

# ---- lists ----
def new_list(name):
    if name in data["lists"]:
        return False
    data["lists"][name] = []
    save()
    return True

def switch(name):
    if name not in data["lists"]:
        return False
    data["current"] = name
    save()
    return True

def rename_list(old, new):
    if old not in data["lists"] or new in data["lists"]:
        return False
    data["lists"][new] = data["lists"].pop(old)
    if data["current"] == old:
        data["current"] = new
    save()
    return True

def delete_list(name):
    if name not in data["lists"] or len(data["lists"]) == 1:
        return False                  # never delete the last list
    del data["lists"][name]
    if data["current"] == name:
        data["current"] = names()[0]
    save()
    return True
