"""Rocky's turtle graphics: a tiny LOGO-style interpreter.

Only these commands exist (never anything the model writes as code):
  FORWARD n / FD n, BACK n / BK n, LEFT n / LT n, RIGHT n / RT n,
  PENUP / PU, PENDOWN / PD, COLOUR name / COLOR name, REPEAT n [ ... ]

draw(text) -> {"segments": [[x1, y1, x2, y2, colour], ...]} in a canvas centred on 0,0
(y up), turtle starting in the middle facing up. Caps keep a bad drawing from hanging
anything: limited tokens, repeats, nesting, steps, segments and canvas size.
"""
import math
import re

CANVAS = 200          # the turtle stays within -200..200 on both axes
MAX_TOKENS = 600
MAX_REPEAT = 72
MAX_DEPTH = 4
MAX_STEPS = 4000      # commands actually run, after repeats
MAX_SEGMENTS = 1500
MAX_MOVE = 400

COLOURS = {
    "black": "#222222", "grey": "#888888", "gray": "#888888", "white": "#ffffff",
    "red": "#e53935", "orange": "#fb8c00", "yellow": "#fdd835", "green": "#43a047",
    "blue": "#1e88e5", "purple": "#8e24aa", "pink": "#ec407a", "brown": "#8d6e63",
    "lightblue": "#81d4fa", "darkgreen": "#2e7d32", "gold": "#ffb300",
}
DEFAULT_COLOUR = "#2f6f6a"

ALIASES = {"FD": "FORWARD", "BK": "BACK", "LT": "LEFT", "RT": "RIGHT", "PU": "PENUP",
           "PD": "PENDOWN", "COLOR": "COLOUR", "BACKWARD": "BACK", "PEN UP": "PENUP"}
NEEDS_NUMBER = {"FORWARD", "BACK", "LEFT", "RIGHT"}

GUIDE = (
    "To draw, write the commands inside <draw>...</draw>. Only these commands work: "
    "FORWARD n, BACK n, LEFT n, RIGHT n (degrees), PENUP, PENDOWN, COLOUR name "
    f"({', '.join(c for c in COLOURS if c != 'gray')}), REPEAT n [ ... ]. "
    "The turtle starts in the middle of a square canvas (200 steps to each edge), facing up. "
    "Keep it simple: under 40 commands, sizes 10 to 150. Examples: a square is "
    "REPEAT 4 [FORWARD 80 RIGHT 90]; a sun is COLOUR yellow REPEAT 36 [FORWARD 10 RIGHT 10]; "
    "PENUP FORWARD 50 PENDOWN moves without drawing."
)


class DrawError(Exception):
    """Something Rocky can say kindly, e.g. "I don't know the command 'JUMP'"."""


def _tokens(text):
    text = re.sub(r"(?i)\bpen\s+(up|down)\b", lambda m: "PEN" + m.group(1).upper(), text or "")
    toks = re.findall(r"\[|\]|[A-Za-z]+|-?\d+(?:\.\d+)?|[^\s\[\]A-Za-z\d]+", text)
    toks = [t for t in toks if not re.fullmatch(r"[,;.:]+", t)]
    if len(toks) > MAX_TOKENS:
        raise DrawError("That's a very long drawing! Try fewer commands.")
    return toks


def _parse(toks, i=0, depth=0):
    """Tokens -> nested list of (command, arg) / ("REPEAT", n, body)."""
    out = []
    while i < len(toks):
        t = toks[i]
        if t == "]":
            if depth == 0:
                raise DrawError("There's a ] without a [ to match it.")
            return out, i + 1
        if t == "[":
            raise DrawError("A [ needs a REPEAT in front of it, like REPEAT 4 [FORWARD 50 RIGHT 90].")
        word = ALIASES.get(t.upper(), t.upper())
        i += 1
        if word in NEEDS_NUMBER:
            if i >= len(toks) or not re.fullmatch(r"-?\d+(?:\.\d+)?", toks[i]):
                raise DrawError(f"{word} needs a number after it, like {word} 50.")
            n = float(toks[i]); i += 1
            if word in ("FORWARD", "BACK") and abs(n) > MAX_MOVE:
                n = math.copysign(MAX_MOVE, n)
            out.append((word, n))
        elif word in ("PENUP", "PENDOWN"):
            out.append((word, None))
        elif word == "COLOUR":
            if i >= len(toks) or toks[i].lower() not in COLOURS:
                raise DrawError("COLOUR needs a colour name, like COLOUR red. I know: "
                                + ", ".join(c for c in COLOURS if c != "gray") + ".")
            out.append((word, COLOURS[toks[i].lower()])); i += 1
        elif word == "REPEAT":
            if i >= len(toks) or not re.fullmatch(r"\d+", toks[i]):
                raise DrawError("REPEAT needs a number, like REPEAT 4 [FORWARD 50 RIGHT 90].")
            n = min(int(toks[i]), MAX_REPEAT); i += 1
            if i >= len(toks) or toks[i] != "[":
                raise DrawError("After REPEAT and its number comes [ ... ], like REPEAT 4 [FORWARD 50 RIGHT 90].")
            if depth + 1 > MAX_DEPTH:
                raise DrawError("Too many REPEATs inside REPEATs!")
            body, i = _parse(toks, i + 1, depth + 1)
            out.append(("REPEAT", n, body))
        else:
            raise DrawError(f"I don't know the command '{t[:20]}'. Try FORWARD, BACK, LEFT, RIGHT, "
                            "PENUP, PENDOWN, COLOUR or REPEAT.")
    if depth:
        raise DrawError("A [ is missing its ] at the end.")
    return out, i


def _clamp(v):
    return max(-CANVAS, min(CANVAS, v))


def draw(text):
    """Run the commands. Returns {"segments": [...]} or raises DrawError."""
    program, _ = _parse(_tokens(text))
    st = {"x": 0.0, "y": 0.0, "h": 90.0, "pen": True, "c": DEFAULT_COLOUR, "steps": 0}
    segs = []

    def run(cmds):
        for cmd in cmds:
            st["steps"] += 1
            if st["steps"] > MAX_STEPS or len(segs) >= MAX_SEGMENTS:
                return False
            if cmd[0] == "REPEAT":
                for _ in range(cmd[1]):
                    if run(cmd[2]) is False:
                        return False
            elif cmd[0] in ("FORWARD", "BACK"):
                d = cmd[1] if cmd[0] == "FORWARD" else -cmd[1]
                x2 = _clamp(st["x"] + d * math.cos(math.radians(st["h"])))
                y2 = _clamp(st["y"] + d * math.sin(math.radians(st["h"])))
                if st["pen"] and (x2, y2) != (st["x"], st["y"]):
                    segs.append([round(st["x"], 1), round(st["y"], 1), round(x2, 1), round(y2, 1), st["c"]])
                st["x"], st["y"] = x2, y2
            elif cmd[0] == "LEFT":
                st["h"] = (st["h"] + cmd[1]) % 360
            elif cmd[0] == "RIGHT":
                st["h"] = (st["h"] - cmd[1]) % 360
            elif cmd[0] == "PENUP":
                st["pen"] = False
            elif cmd[0] == "PENDOWN":
                st["pen"] = True
            elif cmd[0] == "COLOUR":
                st["c"] = cmd[1]
        return True

    run(program)
    if not segs:
        raise DrawError("Nothing got drawn! Start with something like FORWARD 50.")
    return {"segments": segs}


DRAW_RE = re.compile(r"<draw>(.*?)(?:</draw>|$)", re.I | re.S)


def split_reply(reply):
    """'Here you go! <draw>...</draw>' -> ("Here you go!", "...commands..." or None)."""
    m = DRAW_RE.search(reply or "")
    if not m:
        return (reply or "").strip(), None
    text = (reply[:m.start()] + " " + reply[m.end():]).strip()
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text, m.group(1).strip()


def to_svg(drawing, size=400):
    """A plain SVG of a drawing (for checks and saving); the page animates its own."""
    pad = 10
    lines = "".join(
        f'<line x1="{x1}" y1="{-y1}" x2="{x2}" y2="{-y2}" stroke="{c}" />'
        for x1, y1, x2, y2, c in drawing["segments"] if c in COLOURS.values() or c == DEFAULT_COLOUR)
    v = CANVAS + pad
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
            f'viewBox="{-v} {-v} {2 * v} {2 * v}" stroke-width="3" stroke-linecap="round">{lines}</svg>')
