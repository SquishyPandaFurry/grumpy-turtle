"""Talk to a running pond (real model, through the gateway) and print what happens.
Run on the Sprite against a test copy, e.g.:
  python3 scripts/live_test.py http://127.0.0.1:8081 <key> <pond folder of that copy>
"""
import json, sys, time, urllib.error, urllib.request
from pathlib import Path

base, key, pond_dir = sys.argv[1].rstrip("/"), sys.argv[2], Path(sys.argv[3])
visit = "livetest1"
PAUSE = 10  # seconds between messages: new OpenRouter accounts allow 20 model calls a minute


def post(path, body, visit=visit):
    time.sleep(PAUSE)
    req = urllib.request.Request(base + path, data=json.dumps({"visit": visit, **body}).encode(),
                                 headers={"Content-Type": "application/json", "X-Pond-Key": key})
    try:
        return json.load(urllib.request.urlopen(req, timeout=120))
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.read()[:200]!r}"}


def say(room, text, animal="", visit=visit):
    r = post("/talk", {"room": room, "animal": animal, "text": text}, visit)
    print(f"[{room}] child: {text}")
    for x in r.get("replies") or [r]:
        pic = f"  [drew {len(x['drawing']['segments'])} lines]" if x.get("drawing") else ""
        print(f"[{room}] {x.get('name', '?')}: {x.get('reply') or x.get('error')}{pic}")
    print()
    return r


def greet(room, visit=visit):
    r = post("/greet", {"room": room}, visit)
    print(f"[{room}] greeting from {r.get('name', '?')}: {r.get('reply') or r.get('error')}\n")


print("== Greetings (fresh memory)")
for room in ("pond", "turtle", "capybara", "hedgehog"):
    greet(room)

print("== Private chats")
say("turtle", "hi Rocky! my favourite colour is green")
say("turtle", "what did you do today?")
say("turtle", "what's my favourite colour?")
say("capybara", "hello Ferdinand, do you like oranges?")
say("hedgehog", "hello Colin, what's in your collection?")
say("hedgehog", "does anyone know my favourite colour?")

print("== Pond group chat")
say("pond", "hello everyone!")
say("pond", "Ferdinand, where did you go today?")
say("pond", "what do you all do when it gets dark?", animal="hedgehog")

print("== v04: everyone, drawing")
say("pond", "Morning everyone!")
say("pond", "what should we play today?", animal="all")
say("turtle", "Rocky, can you draw me a house?")
say("pond", "Rocky, draw a star for Colin please")
print("[draw] child's own commands:", post("/draw", {"room": "turtle", "commands": "REPEAT 5 [FD 100 RT 144]"}))

print("== New visit: Rocky should still remember green from his memory file")
greet("turtle", visit="livetest2")
say("turtle", "do you remember my favourite colour?", visit="livetest2")

print("== Memory files")
for f in sorted((pond_dir / "memory").glob("*.md")):
    print(f"--- {f.name}\n{f.read_text()}")
