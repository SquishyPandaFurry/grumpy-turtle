# v04 build plan — Rocky draws

Picked 2026-11-27 ("queue a build for 4"): the whole v04 queue. One pull request.

## Items
1. "Everyone" answers in the Pond chat: the chooser can answer "all", so 2-3 animals reply in turn, each seeing the replies before it; an "Everyone" chip next to "Who answers?" (the chip gets all three) — pond-script.md / web-page.md — M
2. Turtle command interpreter → drawing: FORWARD, BACK, LEFT, RIGHT, PENUP, PENDOWN, COLOUR, REPEAT n [ … ] (plus FD/BK/LT/RT/PU/PD), never runs model-written code; caps on commands, repeats and canvas — turtle-drawing.md — M
3. Slow animated drawing on the page, line by line, with a small turtle following the pen — turtle-drawing.md — M
4. Morning picture on wake-up: Rocky draws one picture after the gossip, Colin critiques and Ferdinand loves it, shown in 📰 Pond news — turtle-drawing.md — S
5. Type-your-own-commands box (🖍️ in Rocky's chat and the Pond chat); Rocky draws them and knows he did — turtle-drawing.md — S

## Bugs
- Animals keep reassuring and checking on him — Pond chat is a friendly chat among the animals; not every reply ends in a question to him; no pep talks; greetings don't assume worries.
- Every greeting latches onto the same fact — per visit, at most one greeting may bring up one thing he said (picked by the code, preferring things not brought up recently); every other chat opens with its own news, the gossip or the others.
- Failed wake-up gossip is lost — `last_seen.txt` only moves on once the gossip worked; a failed one is retried on a later visit (at most every 5 minutes).
- Out of credit looks like a hiccup — a 402 / credit or budget error is logged as `OUT OF CREDIT`, the child sees a friendly "the animals are fast asleep, ask a grown-up" message; Pushover ping waits for the connector.

## Not in this batch
Pushover pings (still needs a Pushover connector on the Sprite).
