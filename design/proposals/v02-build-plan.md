# v02 build plan — the full pond

Picked 2026-11-25: the whole v02 queue plus both open bugs. Branch `build/v02`, one pull request.

## Items
1. Capybara and hedgehog personas — personas.md — S
   (draft names until the session with my son; he renames them by editing the first line of each file)
2. Three animal cards, pick-an-animal, auto-choose who answers — web-page.md / pond-script.md — M
3. Shared pond log + pond news panel — pond-script.md / web-page.md — S
   (the log is read into every prompt and shown in the panel; gossip that fills it is v03)
4. "Pond" group chat + private chat per animal — pond-script.md / web-page.md — M
5. Chat history: last 10 messages + running summary of older ones — pond-script.md / web-page.md — M
6. Friendly greeting on page open, using the animal's memory — pond-script.md / web-page.md — S
7. Time of day / day / season in every prompt (UK time) — personas.md / pond-script.md — S
8. Smaller text on phone screens, tablet stays big — web-page.md — S
9. Persona variety: wider pond life, don't repeat recent topics, answer the child first — personas.md — S

## Bugs
- Shelly doesn't remember facts — log the memory call's raw answer and errors, make the persona use its memory, and chat history covers "same chat" recall.
- Tablet keyboard hides the top message — keep the page sized to the visible area when the keyboard opens.

## Not in this batch
Wake-up detection, gossip, last_seen, Pushover, memory summarising (v03); drawing (v04).
