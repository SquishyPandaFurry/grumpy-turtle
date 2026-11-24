"""The pond script: builds the prompt for an animal, calls the model, keeps its memory.

It never runs anything the model writes. Model calls go through the Sprites
connector gateway, so there is no API key in this code or on the Sprite.
"""
import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ANIMALS_DIR = HERE / "animals"
MEMORY_DIR = HERE / "memory"

# One config string, easy to swap.
MODEL = os.environ.get("POND_MODEL", "anthropic/claude-haiku-4.5")

# Gateway: https://api.sprites.dev/v1/gateway/<provider>/<connection_id>/<path>
# The connection ID is not a secret (the gateway only answers this Sprite),
# but it is set by the service, not hard-coded.
CONNECTION_ID = os.environ.get("POND_CONNECTION_ID", "")
GATEWAY_BASE = os.environ.get(
    "POND_GATEWAY_BASE",
    f"https://api.sprites.dev/v1/gateway/openrouter/{CONNECTION_ID}/api/v1",
)

MAX_TEXT = 500           # longest message accepted from the page
MAX_MEMORY_LINE = 120    # longest fact saved to memory
MEMORY_CONTEXT_LINES = 50

MEMORY_PROMPT = (
    "You help a pond animal remember a child it talks to. Read the message the child "
    "just sent and the animal's reply. Is there one lasting fact about the child worth "
    "remembering for a long time (a name they chose, a favourite thing, a pet, an "
    "upcoming event)? Ignore small talk and greetings. Never save private details like "
    "addresses, schools or full names. Answer with ONE short line under 15 words, "
    "written as a fact (e.g. 'His favourite colour is green'), or exactly NONE."
)


class PondError(Exception):
    pass


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


def ask(animal, text):
    """One message to one animal. Returns the animal's reply."""
    _check_animal(animal)
    text = (text or "").strip()[:MAX_TEXT]
    if not text:
        raise PondError("Empty message.")

    memory = read_memory(animal) or "(nothing yet)"
    system = (
        persona(animal)
        + "\n\n## What you remember about the child\n"
        + memory
        + "\n\nStay in character. Reply in plain words only: no lists, no code, no links."
    )
    reply = call_model(
        [{"role": "system", "content": system}, {"role": "user", "content": text}]
    )

    # Second, cheap call: anything worth remembering? A failure here never loses the reply.
    try:
        raw = call_model(
            [
                {"role": "system", "content": MEMORY_PROMPT},
                {"role": "user", "content": f"Child said: {text}\nAnimal replied: {reply}"},
            ],
            max_tokens=40,
        )
        fact = clean_fact(raw)
        if fact:
            append_memory(animal, fact)
    except PondError:
        pass

    return reply
