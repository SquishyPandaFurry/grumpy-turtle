# v03 build plan — the pond lives

Picked 2026-11-25: the whole v03 queue except Pushover (needs a Pushover connector on the Sprite first). Branch `build/v03`, one pull request.

## Items
1. Final names: Rocky the turtle, Ferdinand the capybara, Colin the hedgehog — personas.md — S
2. Character knowledge: `memory/<animal>-pond.md`, what happens between the animals, own prompt heading — personas.md / pond-script.md — S
3. Private chats know the other animals and the Pond chat (this visit's recent messages + summary), never another private chat — pond-script.md — S
4. Memory summarising past ~50 lines (child facts and pond knowledge) — personas.md — S
5. Wake-up detection + gossip: `last_seen.txt`; after 6h quiet, 3–4 lines of gossip go into `pond_log.md` and the animals know they just woke — pond-script.md — M

## Bugs
- Bedtime takes over every chat — the time is background only; bedtime only when he asks, says goodnight, or it's very late.
- Pond chat sounds like one voice — opinions + "how you react to the others" per persona, don't echo the last speaker, a different temperature per animal.
- Tablet keyboard leaves half a screen — while typing, fold the header and cards into a slim bar.

## Not in this batch
Pushover pings (until the connector is set up); drawing (v04).
