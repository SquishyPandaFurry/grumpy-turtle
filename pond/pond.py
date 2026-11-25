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
import time
import urllib.error
import urllib.request
from collections import OrderedDict
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ANIMALS_DIR = HERE / "animals"
MEMORY_DIR = HERE / "memory"
POND_LOG = HERE / "pond_log.md"
LAST_SEEN = HERE / "last_seen.txt"

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
MEMORY_COMPACT_AT = 50   # when a memory file passes this many lines, it is summarised down
MEMORY_COMPACT_TO = 25
WAKE_HOURS = float(os.environ.get("POND_WAKE_HOURS", "6"))   # this long with no visit = a wake-up
WOKE_FRESH_MINUTES = 30  # greetings mention the wake-up for this long after it
GOSSIP_LINES = 4
LOG_CONTEXT_LINES = 10   # pond log lines in every prompt
HISTORY_KEEP = 10        # messages of the chat shown word for word
HISTORY_ROLL_AT = 16     # when a chat passes this, older messages are rolled into the summary
MAX_VISITS = 30          # chats kept in memory (a reload starts a fresh visit)

POND_ROOM = "pond"
FACES = {"turtle": "🐢", "capybara": "🦫", "hedgehog": "🦔"}
KINDS = {"turtle": "turtle", "capybara": "capybara", "hedgehog": "hedgehog"}
# A different temperature per animal, so they don't all sound alike.
TEMPERATURES = {"turtle": 0.6, "capybara": 0.85, "hedgehog": 1.0}

MEMORY_PROMPT = (
    "You help a pond animal remember things. Read what the child just said and the animal's "
    "reply, then answer with exactly two lines.\n"
    "Line 1 starts 'CHILD:' and gives one NEW lasting fact about the child worth remembering "
    "(something they like or dislike, a favourite thing, a name they gave something, a pet, a "
    "friend's first name, something they did or will do soon), written as a fact "
    "(e.g. 'CHILD: His favourite colour is green'), or 'CHILD: NONE'. Only facts about the CHILD, "
    "never about the animal or the pond. Ignore greetings, questions and small talk, and anything "
    "already in the known facts. Never save private details like addresses, schools or full names.\n"
    "Line 2 starts 'POND:' and gives one NEW thing that happened between the pond animals, written "
    "from this animal's side (e.g. 'POND: Colin is cross that Ferdinand took the warm rock'), or "
    "'POND: NONE'. Only real events or feelings between the animals, not plans for the child, and "
    "nothing already in the known pond events.\n"
    "Each line under 15 words."
)

COMPACT_PROMPT = (
    "Here is a pond animal's list of remembered {what}, oldest first. Rewrite it as a shorter list "
    "of at most {n} lines: merge repeats, drop what no longer matters, keep favourite things, names "
    "and the most recent events. One short fact per line, each line starting '- '. Nothing else."
)

GOSSIP_PROMPT = (
    "Three pond animals have been alone for {hours} while the child was away. First write one line "
    "'REMEMBER: ' and the one thing that happened between them, under 15 words. Then write the gossip "
    "they had: {lines} short lines (one or two sentences each), taking turns, each line "
    "'Name: what they said' (names: {names}). Each animal sounds like itself and has its own opinion: "
    "they tease, disagree and change the subject, they don't just agree. Carry on from what happened "
    "before. Gentle, funny, fine for a young child; no talk of bedtime."
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
    """'Rocky the turtle' -> 'Rocky'."""
    return display_name(animal).split(" the ")[0].strip() or animal


def face(animal):
    return FACES.get(animal, "🐾")


def animal_info():
    return [{"id": a, "name": short_name(a), "full": display_name(a), "face": face(a)}
            for a in list_animals()]


def _memory_path(animal, kind="child"):
    return MEMORY_DIR / (f"{animal}.md" if kind == "child" else f"{animal}-pond.md")


def read_memory(animal, kind="child"):
    """kind "child": facts about the child (memory/<animal>.md).
    kind "pond": what happened between the animals (memory/<animal>-pond.md)."""
    path = _memory_path(animal, kind)
    if not path.exists():
        return ""
    lines = path.read_text(encoding="utf-8").splitlines()
    return "\n".join(lines[-MEMORY_CONTEXT_LINES:])


_memory_lock = threading.Lock()


def append_memory(animal, fact, kind="child"):
    MEMORY_DIR.mkdir(exist_ok=True)
    with _memory_lock:
        path = _memory_path(animal, kind)
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"- {fact}\n")
        _compact(path, kind)


def _compact(path, kind):
    """When a memory file passes ~50 lines, summarise it down. A copy of the old file is kept
    as <name>.bak, and if the summary looks wrong the file is left as it was."""
    lines = [l for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    if len(lines) <= MEMORY_COMPACT_AT:
        return
    what = "facts about a child" if kind == "child" else "things that happened between the pond animals"
    try:
        raw = call_model(
            [{"role": "system", "content": COMPACT_PROMPT.format(what=what, n=MEMORY_COMPACT_TO)},
             {"role": "user", "content": "\n".join(lines)}],
            max_tokens=600,
        )
    except PondError as e:
        log(f"compact {path.name}: error: {e}")
        return
    new = []
    for l in raw.splitlines():
        fact = _clean_line(l)
        if fact:
            new.append(f"- {fact}")
    if not (5 <= len(new) <= MEMORY_COMPACT_TO + 5):
        log(f"compact {path.name}: kept as it was ({len(new)} lines back)")
        return
    path.with_name(path.name + ".bak").write_text("\n".join(lines) + "\n", encoding="utf-8")
    path.write_text("\n".join(new) + "\n", encoding="utf-8")
    log(f"compact {path.name}: {len(lines)} -> {len(new)} lines")


def append_pond_log(lines):
    with open(POND_LOG, "a", encoding="utf-8") as f:
        for line in lines:
            f.write(f"- {line}\n")


def read_pond_log(n=LOG_CONTEXT_LINES):
    if not POND_LOG.exists():
        return []
    lines = [l.strip() for l in POND_LOG.read_text(encoding="utf-8").splitlines() if l.strip()]
    return lines[-n:]


_NOT_A_FACT = re.compile(
    r"^(none|nothing|no\b|n/a)|no (new )?(lasting )?facts?|nothing (new|worth)|the animal|"
    r"pond animal|already (known|saved|remembered)", re.I)


def _clean_line(raw):
    """One safe, short line from a model answer, or None for NONE / an explanation."""
    if not raw or not raw.strip():
        return None
    line = raw.strip().splitlines()[0].strip()
    line = line.lstrip("-*• ").strip().strip('"').strip()
    line = re.sub(r"^(CHILD|POND)\s*:\s*", "", line, flags=re.I)
    line = re.sub(r"[\x00-\x1f<>`]", "", line)
    bare = line.strip("()[]{}'\"*_ .!").strip()
    if not bare or _NOT_A_FACT.search(bare):
        return None
    if len(line.split()) > 20 or len(line) > MAX_MEMORY_LINE:
        return None   # an explanation, not a short fact
    return line


def clean_fact(raw, animal=None):
    """Turn the model's memory answer into one safe line about the child, or None."""
    line = _clean_line(raw)
    if line and animal and re.search(rf"\b{re.escape(short_name(animal))}\b", line, re.I):
        return None   # a fact about the animal itself, not about the child
    return line


def split_memory_answer(raw):
    """The memory call answers 'CHILD: ...' and 'POND: ...'. Returns (child_raw, pond_raw).
    An answer without labels is taken as the child line (older prompt style)."""
    child = pond_ = None
    for l in (raw or "").splitlines():
        l = l.strip().lstrip("-*• ").strip()
        m = re.match(r"(CHILD|POND)\s*:\s*(.*)", l, re.I)
        if m and m.group(1).upper() == "CHILD":
            child = m.group(2)
        elif m:
            pond_ = m.group(2)
    if child is None and pond_ is None:
        child = raw
    return child, pond_


def clean_pond_fact(raw):
    """A line about what happened between the animals, or None."""
    line = _clean_line(raw)
    if line and re.search(r"\b(child|he told me|address|school)\b", line, re.I):
        return None   # that's about the child, not the animals
    return line


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
        part = "evening, near his bedtime"
    elif h < 21:
        part = "late evening"
    else:
        part = "night-time (very late for him)"
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

RETRY_WAITS = [float(x) for x in os.environ.get("POND_RETRY_WAITS", "3,8").split(",") if x]


def call_model(messages, max_tokens=300, temperature=None):
    """Model call; on a rate limit (429) waits a few seconds and tries again."""
    for wait in RETRY_WAITS + [None]:
        try:
            return _call_model(messages, max_tokens, temperature)
        except RateLimited as e:
            if wait is None:
                raise PondError(str(e)) from e
            log(f"rate limited, retrying in {wait:g}s")
            time.sleep(wait)


class RateLimited(Exception):
    pass


def _call_model(messages, max_tokens=300, temperature=None):
    if not CONNECTION_ID and "POND_GATEWAY_BASE" not in os.environ:
        raise PondError("POND_CONNECTION_ID is not set.")
    payload = {"model": MODEL, "messages": messages, "max_tokens": max_tokens}
    if temperature is not None:
        payload["temperature"] = temperature
    body = json.dumps(payload).encode()
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
        if e.code == 429:
            raise RateLimited(f"Gateway said 429: {detail}") from e
        raise PondError(f"Gateway said {e.code}: {detail}") from e
    except (urllib.error.URLError, TimeoutError) as e:
        raise PondError(f"Could not reach the gateway: {e}") from e
    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError, AttributeError) as e:
        raise PondError(f"Unexpected reply from the model: {str(data)[:300]}") from e


def _pond_chat_view(visit):
    """What a private chat may see of this visit's Pond group chat (never another private chat)."""
    with _lock:
        pond_chat = _chats.get((visit, POND_ROOM))
    if not pond_chat or not (pond_chat["messages"] or pond_chat["summary"]):
        return "(nothing said there yet this time)"
    parts = []
    if pond_chat["summary"]:
        parts.append("Summary: " + pond_chat["summary"])
    if pond_chat["messages"]:
        parts.append(_transcript(pond_chat["messages"][-HISTORY_KEEP:]))
    return "\n".join(parts)


def _system_prompt(animal, room, chat, visit="default"):
    memory = read_memory(animal) or "(nothing yet)"
    pond_memory = read_memory(animal, "pond") or "(nothing special yet)"
    pond_log = "\n".join(read_pond_log()) or "(all quiet)"
    others = ", ".join(display_name(a) for a in list_animals() if a != animal)
    if room == POND_ROOM:
        where = (f"This is the Pond group chat: the child, you, and the others ({others}) can all "
                 "see it. Lines are labelled with who said them. You only speak for yourself.\n"
                 "You are your own animal with your own opinions. Don't echo, repeat or just agree "
                 "with what the last animal said: react your own way (disagree, tease, add your own "
                 "take, or bring up something different), and still answer the child.")
    else:
        where = (f"This is a private chat between just you and the child. The others ({others}) "
                 "live in the pond with you and you can talk about them. You know what was said in "
                 "the Pond group chat (below). You never see the child's private chats with the others: "
                 "if he asks what he told one of them, say kindly that you don't know, that's between them."
                 "\n\nThe Pond group chat this visit:\n" + _pond_chat_view(visit))
    return (
        persona(animal)
        + "\n\n## What you remember about the child\n"
        + "These are true things he told you before. Use them: if he asks about one, you remember it.\n"
        + memory
        + "\n\n## What has happened between you and the other animals\n"
        + pond_memory
        + "\n\n## Right now\n" + time_of_day()
        + " This is background only, so your world matches his (dark evenings, frosty mornings...). "
        + "Don't bring up bedtime, sleep or how late it is unless he asks, says goodnight, or it's "
        + "very late at night, and then only once. Otherwise follow what he's talking about."
        + "\n\n## Pond news\n" + pond_log
        + "\n\n## This chat\n" + where
        + ("\nSummary of earlier in this chat: " + chat["summary"] if chat["summary"] else "")
        + "\n\n## How to answer\n"
        + "- Answer what the child actually said first, and stay on his topic.\n"
        + "- Don't repeat a topic, phrase or opening you used in your recent messages (bedtime and sleep count as a topic); pick something new from your pond life.\n"
        + "- Stay in character. Reply in plain words only: no lists, no code, no links, and don't start with your name."
    )


def _strip_name(animal, reply):
    for label in (short_name(animal), display_name(animal)):
        if reply.lower().startswith(label.lower() + ":"):
            return reply[len(label) + 1:].strip()
    return reply


def _remember(animal, text, reply, room=None):
    """Second, cheap call: anything worth remembering? A failure here never loses the reply,
    but it is always logged so we can see why something wasn't saved."""
    try:
        raw = call_model(
            [{"role": "system", "content": MEMORY_PROMPT},
             {"role": "user", "content": f"Known facts:\n{read_memory(animal) or '(none)'}\n\n"
                                         f"Known pond events:\n{read_memory(animal, 'pond') or '(none)'}\n\n"
                                         f"Child said: {text}\n{short_name(animal)} replied: {reply}"}],
            max_tokens=80,
        )
    except PondError as e:
        log(f"memory {animal}: error: {e}")
        return
    child_raw, pond_raw = split_memory_answer(raw)
    fact = clean_fact(child_raw, animal)
    # Pond events are only taken from the Pond group chat, so nothing from a private chat
    # can reach the gossip that all three animals share.
    pond_fact = clean_pond_fact(pond_raw) if pond_raw is not None and room == POND_ROOM else None
    log(f"memory {animal}: {'saved' if fact else 'nothing'}, pond {'saved' if pond_fact else 'nothing'} "
        f"(model said {raw[:120]!r})")
    if fact:
        append_memory(animal, fact)
    if pond_fact:
        append_memory(animal, pond_fact, "pond")


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
    check_wake()
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
            [{"role": "system", "content": _system_prompt(animal, room, chat, visit)},
             {"role": "user", "content": user}], temperature=TEMPERATURES.get(animal)))

        chat["messages"] += [("child", text), (animal, reply)]
        _remember(animal, text, reply, room)
        _roll_summary(chat)
    return animal, reply


def greet(visit="default", room=POND_ROOM):
    """The friendly hello when a chat opens, using the animal's memory. Returns (animal, reply)."""
    _check_room(room)
    check_wake()
    chat = _chat(visit, room)
    with chat["lock"]:
        if chat["messages"]:   # already greeted in this visit
            s, t = next(((s, t) for s, t in chat["messages"] if s != "child"), chat["messages"][0])
            return s, t
        animal = room if room != POND_ROOM else random.choice(list_animals())
        user = ("The child has just opened the chat. Greet him like a friend would, in one or two "
                "short sentences. If you remember something about him, ask about ONE of those things "
                "(not always the same one). Don't list what you remember.")
        hours = woke_recently()
        if hours:
            user += (f" The pond has just woken up: nobody visited for about {hours} hours. You can say "
                     "you've missed him, or share one bit of the gossip from the pond news.")
        reply = _strip_name(animal, call_model(
            [{"role": "system", "content": _system_prompt(animal, room, chat, visit)},
             {"role": "user", "content": user}], max_tokens=120,
            temperature=TEMPERATURES.get(animal)))
        chat["messages"].append((animal, reply))
    return animal, reply


# ---------- wake-up and gossip ----------

_wake_lock = threading.Lock()
_woke = {"at": 0.0, "hours": 0}


def woke_recently():
    """Hours the pond slept, if it woke in the last half hour, else 0."""
    if _woke["hours"] and time.time() - _woke["at"] < WOKE_FRESH_MINUTES * 60:
        return _woke["hours"]
    return 0


def check_wake(now=None):
    """Called on every visit. If nobody came for WAKE_HOURS, the animals gossip first.
    Returns the hours slept when this call woke the pond, else 0."""
    now = now or time.time()
    with _wake_lock:
        try:
            last = float(LAST_SEEN.read_text().strip())
        except (OSError, ValueError):
            last = None   # first start: nothing to wake from
        try:
            LAST_SEEN.write_text(f"{now:.0f}\n")
        except OSError as e:
            log(f"last_seen: {e}")
        if last is None or now - last < WAKE_HOURS * 3600:
            return 0
        hours = round((now - last) / 3600)
        log(f"wake-up after {hours}h: gossip")
        _woke.update(at=now, hours=hours)
        try:
            gossip(hours)
        except PondError as e:
            log(f"gossip error: {e}")
        return hours


def _gossip_context(hours):
    parts = [time_of_day(), f"They have been alone for about {hours} hours."]
    for a in list_animals():
        text = (ANIMALS_DIR / f"{a}.md").read_text(encoding="utf-8")
        keep = re.split(r"\n## Rules", text)[0]
        parts.append(keep.strip())
        parts.append(f"What {short_name(a)} remembers happening between the animals:\n"
                     + (read_memory(a, "pond") or "(nothing yet)"))
    parts.append("Earlier pond news:\n" + ("\n".join(read_pond_log(6)) or "(all quiet)"))
    # The agreed design lets gossip borrow one harmless thing an animal knows about the child.
    facts = [(a, l.lstrip("- ").strip()) for a in list_animals()
             for l in read_memory(a).splitlines() if l.strip()]
    if facts and random.random() < 0.5:
        a, fact = random.choice(facts)
        parts.append(f"{short_name(a)} knows this about the child and may mention it kindly: {fact}")
    return "\n\n".join(parts)


def parse_gossip(raw):
    """Model gossip -> (lines like 'Colin: ...', remember line or None). Unknown speakers dropped."""
    names = {short_name(a).lower(): a for a in list_animals()}
    lines, remember = [], None
    for l in (raw or "").splitlines():
        l = l.strip().lstrip("-*• ").strip().replace("**", "")
        m = re.match(r"([A-Za-z]+)\s*:\s*(.+)", l)
        if not m:
            continue
        who, said = m.group(1), re.sub(r"[\x00-\x1f<>`]", "", m.group(2)).strip()
        if who.upper() == "REMEMBER":
            remember = clean_pond_fact(said)
        elif who.lower() in names and said and len(said) <= 240 and len(lines) < GOSSIP_LINES:
            lines.append(f"{short_name(names[who.lower()])}: {said}")
    return lines, remember


def gossip(hours=WAKE_HOURS):
    """3-4 lines of gossip between the animals into pond_log.md; the gist goes into each
    animal's pond memory so they can carry on from it later."""
    names = ", ".join(short_name(a) for a in list_animals())
    raw = call_model(
        [{"role": "system", "content": GOSSIP_PROMPT.format(
            hours=f"{hours} hours", lines="3 or 4", names=names)},
         {"role": "user", "content": _gossip_context(hours)}],
        max_tokens=500, temperature=1.0,
    )
    lines, remember = parse_gossip(raw)
    log(f"gossip: {len(lines)} lines, remember {'yes' if remember else 'no'}")
    if len(lines) < 2:
        log(f"gossip: unusable answer {raw[:120]!r}")
        return []
    append_pond_log(lines)
    if remember:
        for a in list_animals():
            append_memory(a, remember, "pond")
    return lines
