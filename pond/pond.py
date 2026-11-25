"""The pond script: builds the prompt for an animal, calls the model, keeps its memory.

It never runs anything the model writes. Model calls go through the Sprites
connector gateway, so there is no API key in this code or on the Sprite.
"""
import json
import os
import random
import re
import sys
import threading
import urllib.error
import urllib.request
from collections import OrderedDict
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ANIMALS_DIR = HERE / "animals"
MEMORY_DIR = HERE / "memory"
POND_LOG = HERE / "pond_log.md"

# One config string, easy to swap.
MODEL = os.environ.get("POND_MODEL", "anthropic/claude-haiku-4.5")

# Gateway: https://api.sprites.dev/v1/gateway/<provider>/<connection_id>/<path>
# The connection ID is not a secret (the gateway only answers this Sprite),
# but it is set by the service, not hard-coded.
CONNECTION_ID = os.environ.get("POND_CONNECTION_ID", "")
GATEWAY_BASE = os.environ.get(
    "POND_GATEWAY_BASE",
    f"https://api.sprites.dev/v1/gateway/openrouter/{CONNECTION_ID}/v1",
)

MAX_TEXT = 500           # longest message accepted from the page
MAX_MEMORY_LINE = 120    # longest fact saved to memory
MEMORY_CONTEXT_LINES = 50
LOG_CONTEXT_LINES = 10   # pond log lines in every prompt
HISTORY_KEEP = 10        # messages of the chat shown word for word
HISTORY_ROLL_AT = 16     # when a chat passes this, older messages are rolled into the summary
MAX_VISITS = 30          # chats kept in memory (a reload starts a fresh visit)

POND_ROOM = "pond"
FACES = {"turtle": "🐢", "capybara": "🦫", "hedgehog": "🦔"}
KINDS = {"turtle": "turtle", "capybara": "capybara", "hedgehog": "hedgehog"}

MEMORY_PROMPT = (
    "You help a pond animal remember a child it talks to. Read what the child just said "
    "and the animal's reply. Is there one NEW lasting fact about the child worth "
    "remembering (something they like or dislike, a favourite thing, a name they gave "
    "something, a pet, a friend's first name, something they did or will do soon)? "
    "Ignore greetings and small talk, and anything already in the list of known facts. "
    "Never save private details like addresses, schools or full names. Answer with ONE "
    "short line under 15 words, written as a fact (e.g. 'His favourite colour is green'), "
    "or exactly NONE."
)

SUMMARY_PROMPT = (
    "You keep a short running summary of a chat between a young child and pond animals. "
    "Add the new messages to the summary. Keep what was talked about and anything the "
    "child asked or told. At most 5 short sentences. Plain words only."
)

CHOOSE_PROMPT = (
    "Three pond animals share a group chat with a young child: {names}. "
    "Read the chat and the child's new message and pick who should answer, so it fits "
    "what he said and the animals take turns. Answer with exactly one word: {ids}."
)


class PondError(Exception):
    pass


def log(msg):
    sys.stderr.write(msg + "\n")
    sys.stderr.flush()


# ---------- animals, memory, pond log ----------

def list_animals():
    return sorted(p.stem for p in ANIMALS_DIR.glob("*.md") if p.stem != "rules")


def _check_animal(animal):
    if animal not in list_animals():
        raise PondError(f"No animal called {animal!r} in the pond.")


def persona(animal):
    _check_animal(animal)
    text = (ANIMALS_DIR / f"{animal}.md").read_text(encoding="utf-8")
    rules = (ANIMALS_DIR / "rules.md").read_text(encoding="utf-8").strip()
    return text.replace("(shared rules block)", rules)


def display_name(animal):
    first = (ANIMALS_DIR / f"{animal}.md").read_text(encoding="utf-8").splitlines()[0]
    return first.lstrip("# ").strip() or animal


def short_name(animal):
    """'Shelly the turtle' -> 'Shelly'."""
    return display_name(animal).split(" the ")[0].strip() or animal


def face(animal):
    return FACES.get(animal, "🐾")


def animal_info():
    return [{"id": a, "name": short_name(a), "full": display_name(a), "face": face(a)}
            for a in list_animals()]


def read_memory(animal):
    path = MEMORY_DIR / f"{animal}.md"
    if not path.exists():
        return ""
    lines = path.read_text(encoding="utf-8").splitlines()
    return "\n".join(lines[-MEMORY_CONTEXT_LINES:])


def append_memory(animal, fact):
    MEMORY_DIR.mkdir(exist_ok=True)
    with open(MEMORY_DIR / f"{animal}.md", "a", encoding="utf-8") as f:
        f.write(f"- {fact}\n")


def read_pond_log(n=LOG_CONTEXT_LINES):
    if not POND_LOG.exists():
        return []
    lines = [l.strip() for l in POND_LOG.read_text(encoding="utf-8").splitlines() if l.strip()]
    return lines[-n:]


def clean_fact(raw):
    """Turn the model's memory answer into one safe line, or None."""
    if not raw:
        return None
    line = raw.strip().splitlines()[0].strip() if raw.strip() else ""
    line = line.lstrip("-*• ").strip().strip('"').strip()
    if not line or line.upper().rstrip(".") == "NONE":
        return None
    line = re.sub(r"[\x00-\x1f<>`]", "", line)
    return line[:MAX_MEMORY_LINE] or None


# ---------- time of day (UK) ----------

def _last_sunday(year, month):
    d = datetime(year, month + 1, 1, tzinfo=timezone.utc) - timedelta(days=1) if month < 12 \
        else datetime(year, 12, 31, tzinfo=timezone.utc)
    return d - timedelta(days=(d.weekday() + 1) % 7)


def uk_now(now_utc=None):
    """UK local time without needing tzdata: BST from 01:00 UTC on the last Sunday
    of March to 01:00 UTC on the last Sunday of October."""
    now = now_utc or datetime.now(timezone.utc)
    start = _last_sunday(now.year, 3).replace(hour=1)
    end = _last_sunday(now.year, 10).replace(hour=1)
    return now + timedelta(hours=1) if start <= now < end else now


# Rough UK sunrise / sunset (local hour) by month, enough to say "it's dark".
_SUN = {1: (8, 16.25), 2: (7.5, 17.25), 3: (6.5, 18.25), 4: (6.5, 20), 5: (5.5, 20.75),
        6: (4.75, 21.33), 7: (5, 21.25), 8: (5.75, 20.5), 9: (6.5, 19.33), 10: (7.25, 18.25),
        11: (7.25, 16.25), 12: (8, 15.9)}


def time_of_day(now_utc=None):
    """One line about the child's world right now (UK time, day, season, light)."""
    t = uk_now(now_utc)
    h = t.hour + t.minute / 60
    weekend = t.weekday() >= 5
    if h < 5:
        part = "the middle of the night (he should be asleep!)"
    elif h < 8:
        part = "early morning"
    elif h < 12:
        part = "morning"
    elif h < 13.5:
        part = "lunchtime"
    elif h < 15:
        part = "afternoon"
    elif h < 17.5:
        part = "afternoon" if weekend else "after school"
    elif h < 19:
        part = "evening, around teatime"
    elif h < 20.5:
        part = "bedtime"
    else:
        part = "night-time (late for him)"
    season = {12: "winter", 1: "winter", 2: "winter", 3: "spring", 4: "spring", 5: "spring",
              6: "summer", 7: "summer", 8: "summer"}.get(t.month, "autumn")
    rise, sets = _SUN[t.month]
    light = "dark outside" if (h < rise or h >= sets) else "daylight"
    day = t.strftime("%A")
    kind = "the weekend" if weekend else "a school day"
    return (f"In the child's world (UK) it is {day} ({kind}), {t.strftime('%H:%M')}, "
            f"{part}, {season}, {light}.")


# ---------- chats: last 10 messages + running summary, per visit and room ----------

_chats = OrderedDict()   # (visit, room) -> {"messages": [(speaker, text)], "summary": str}
_lock = threading.Lock()


def _chat(visit, room):
    key = (visit, room)
    with _lock:
        if key not in _chats:
            _chats[key] = {"messages": [], "summary": "", "lock": threading.Lock()}
            visits = list(OrderedDict.fromkeys(v for v, _ in _chats))
            for old in visits[:-MAX_VISITS]:
                for k in [k for k in _chats if k[0] == old]:
                    del _chats[k]
        _chats.move_to_end(key)
        return _chats[key]


def _speaker_label(speaker):
    return "Child" if speaker == "child" else short_name(speaker)


def _transcript(messages):
    return "\n".join(f"{_speaker_label(s)}: {t}" for s, t in messages)


def _roll_summary(chat):
    """Fold the oldest messages into the running summary, keeping the last 10."""
    if len(chat["messages"]) <= HISTORY_ROLL_AT:
        return
    old, keep = chat["messages"][:-HISTORY_KEEP], chat["messages"][-HISTORY_KEEP:]
    try:
        summary = call_model(
            [{"role": "system", "content": SUMMARY_PROMPT},
             {"role": "user", "content": f"Summary so far: {chat['summary'] or '(none)'}\n\n"
                                         f"New messages:\n{_transcript(old)}"}],
            max_tokens=200,
        )
    except PondError as e:
        log(f"summary error: {e}")
        # Keep a plain fallback so nothing is lost.
        summary = (chat["summary"] + " " + " ".join(t for _, t in old))[-1200:]
    chat["summary"] = summary.strip()
    chat["messages"] = keep


# ---------- model calls ----------

def call_model(messages, max_tokens=300):
    if not CONNECTION_ID and "POND_GATEWAY_BASE" not in os.environ:
        raise PondError("POND_CONNECTION_ID is not set.")
    body = json.dumps({"model": MODEL, "messages": messages, "max_tokens": max_tokens}).encode()
    req = urllib.request.Request(
        GATEWAY_BASE.rstrip("/") + "/chat/completions",
        data=body,
        headers={"Content-Type": "application/json"},  # no Authorization: the gateway adds it
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as e:
        detail = e.read()[:300].decode(errors="replace")
        raise PondError(f"Gateway said {e.code}: {detail}") from e
    except (urllib.error.URLError, TimeoutError) as e:
        raise PondError(f"Could not reach the gateway: {e}") from e
    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError, AttributeError) as e:
        raise PondError(f"Unexpected reply from the model: {str(data)[:300]}") from e


def _system_prompt(animal, room, chat):
    memory = read_memory(animal) or "(nothing yet)"
    pond_log = "\n".join(read_pond_log()) or "(all quiet)"
    if room == POND_ROOM:
        others = ", ".join(display_name(a) for a in list_animals() if a != animal)
        where = (f"This is the Pond group chat: the child, you, and the others ({others}) can all "
                 "see it. Lines are labelled with who said them. You only speak for yourself.")
    else:
        where = "This is a private chat between just you and the child."
    return (
        persona(animal)
        + "\n\n## What you remember about the child\n"
        + "These are true things he told you before. Use them: if he asks about one, you remember it.\n"
        + memory
        + "\n\n## Right now\n" + time_of_day()
        + " Let your world match it (dark winter evenings, sleepy at bedtime, frosty mornings...)."
        + "\n\n## Pond news\n" + pond_log
        + "\n\n## This chat\n" + where
        + ("\nSummary of earlier in this chat: " + chat["summary"] if chat["summary"] else "")
        + "\n\n## How to answer\n"
        + "- Answer what the child actually said first.\n"
        + "- Don't repeat a topic, phrase or opening you used in your recent messages; pick something new from your pond life.\n"
        + "- Stay in character. Reply in plain words only: no lists, no code, no links, and don't start with your name."
    )


def _strip_name(animal, reply):
    for label in (short_name(animal), display_name(animal)):
        if reply.lower().startswith(label.lower() + ":"):
            return reply[len(label) + 1:].strip()
    return reply


def _remember(animal, text, reply):
    """Second, cheap call: anything worth remembering? A failure here never loses the reply,
    but it is always logged so we can see why something wasn't saved."""
    try:
        raw = call_model(
            [{"role": "system", "content": MEMORY_PROMPT},
             {"role": "user", "content": f"Known facts:\n{read_memory(animal) or '(none)'}\n\n"
                                         f"Child said: {text}\nAnimal replied: {reply}"}],
            max_tokens=40,
        )
    except PondError as e:
        log(f"memory {animal}: error: {e}")
        return
    fact = clean_fact(raw)
    log(f"memory {animal}: {'saved' if fact else 'nothing'} (model said {raw[:80]!r})")
    if fact:
        append_memory(animal, fact)


def choose_animal(text, chat):
    """Who answers in the Pond chat when nobody was picked."""
    animals = list_animals()
    low = text.lower()
    named = [a for a in animals
             if re.search(rf"\b({re.escape(short_name(a).lower())}|{KINDS.get(a, a)})\b", low)]
    if len(named) == 1:
        return named[0]
    last = next((s for s, _ in reversed(chat["messages"]) if s != "child"), None)
    try:
        raw = call_model(
            [{"role": "system", "content": CHOOSE_PROMPT.format(
                names=", ".join(f"{display_name(a)} ({a})" for a in animals),
                ids=" or ".join(animals))},
             {"role": "user", "content": f"{_transcript(chat['messages'][-6:])}\nChild: {text}"}],
            max_tokens=5,
        )
        pick = re.sub(r"[^a-z]", "", raw.lower())
        if pick in animals:
            return pick
        log(f"choose: unexpected answer {raw[:40]!r}")
    except PondError as e:
        log(f"choose error: {e}")
    return random.choice([a for a in animals if a != last] or animals)


def _check_room(room):
    if room != POND_ROOM:
        _check_animal(room)


def ask(animal, text, visit="default", room=None):
    """One message from the child in a chat. Returns (animal, reply).

    room is "pond" (group chat) or an animal id (private chat). In the Pond chat,
    animal may be None/"" and one is chosen."""
    room = room or animal
    _check_room(room)
    text = (text or "").strip()[:MAX_TEXT]
    if not text:
        raise PondError("Empty message.")
    chat = _chat(visit, room)
    with chat["lock"]:
        if room != POND_ROOM:
            animal = room
        elif not animal:
            animal = choose_animal(text, chat)
        _check_animal(animal)

        recent = _transcript(chat["messages"]) or "(nothing yet)"
        user = (f"Last messages in this chat:\n{recent}\n\n"
                f"The child just said: {text}\n\nReply as {short_name(animal)}.")
        reply = _strip_name(animal, call_model(
            [{"role": "system", "content": _system_prompt(animal, room, chat)},
             {"role": "user", "content": user}]))

        chat["messages"] += [("child", text), (animal, reply)]
        _remember(animal, text, reply)
        _roll_summary(chat)
    return animal, reply


def greet(visit="default", room=POND_ROOM):
    """The friendly hello when a chat opens, using the animal's memory. Returns (animal, reply)."""
    _check_room(room)
    chat = _chat(visit, room)
    with chat["lock"]:
        if chat["messages"]:   # already greeted in this visit
            s, t = next(((s, t) for s, t in chat["messages"] if s != "child"), chat["messages"][0])
            return s, t
        animal = room if room != POND_ROOM else random.choice(list_animals())
        user = ("The child has just opened the chat. Greet him like a friend would, in one or two "
                "short sentences. If you remember something about him, ask about ONE of those things "
                "(not always the same one). Fit the time of day. Don't list what you remember.")
        reply = _strip_name(animal, call_model(
            [{"role": "system", "content": _system_prompt(animal, room, chat)},
             {"role": "user", "content": user}], max_tokens=120))
        chat["messages"].append((animal, reply))
    return animal, reply
