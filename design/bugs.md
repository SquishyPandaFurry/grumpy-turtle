# Bugs

## Open
- **Animals keep reassuring and checking on him** (v03, found 2026-11-26). In the Pond chat every reply turns back to the child with a question or a pep talk, and they hardly react to each other, so it feels like three carers taking turns. Expected: a friendly chat at the pond; the animals talk among themselves (agree, tease, carry on their own little dramas from pond news) and he joins in. Not every reply ends in a question to him. Greetings mustn't assume worries (Colin's "trouble sleeping again?"). — personas.md / pond-script.md
- **Everyone latches onto the same fact** (v03, found 2026-11-27). The morning after he mentioned kickboxing and school, every greeting (Pond chat and all three private chats) asked about kickboxing and school. Same pattern as the old bedtime bug. Expected: at most one animal brings up a given thing he said per visit; the others open with their own news, the gossip, or each other. — pond-script.md / personas.md
- **Failed wake-up gossip is lost** (v03, found 2026-11-27). `check_wake()` writes `last_seen.txt` before `gossip()` runs, so when gossip fails (out of credit at 06:17) the pond counts as visited and never tries again. Expected: only mark the wake-up done once gossip succeeds, or retry it on the next visit. — pond-script.md
- **Out of credit looks like a hiccup** (v03, found 2026-11-27). OpenRouter 402 "exceeds your available credits" shows the same "The pond is a bit sleepy" as any glitch, and nothing tells the grown-up. Expected: log it clearly as out of credit, keep the child's message friendly, and (once Pushover exists) ping the phone once. — infra-connectors.md / pond-script.md

## Fixed
- v03 (2026-11-26): bedtime takes over every chat, Pond chat sounds like one voice, tablet keyboard leaves half a screen (folds the top while typing; check on the real tablet).
- v02 (2026-11-25): Shelly not remembering (chat history + memory logging + non-fact filter; tested on the Sprite) and tablet keyboard hiding the top message (app pinned to the visible viewport).

## Was open
- **Shelly doesn't remember facts** (v01, found 2026-11-24). Told "my favourite colour is green", she doesn't remember it later, not even in the same chat. Expected: one line in `pond/memory/turtle.md`. Note: `ask()` in `pond/pond.py` silently ignores any failure of the memory call, so the cause is hidden; check the memory file on the Sprite and log the error. — pond-script.md
  - Checked on the Sprite 2026-11-24 20:25: `turtle.md` does hold "Favourite colour is green." (written 20:09) and the memory call works when run by hand. Only 2 facts saved from ~16 messages; no errors in the service log, but memory-call errors and NONE answers are never logged, so we can't tell which messages failed. Still unclear why she didn't use the saved fact when asked. Next step: log the memory call's raw answer and any error, then retest "favourite colour" → ask again.
- **Tablet keyboard hides the top message** (v01, found 2026-11-24). When the on-screen keyboard opens, it pushes the top of the page off screen so the latest/top message can't be read. — web-page.md
