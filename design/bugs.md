# Bugs

## Open
- **Bedtime takes over every chat** (v02, found 2026-11-25). In the evening, whatever he talks about (hot chocolate, oranges…), the animals keep steering back to bedtime and sleeping because it's late. Expected: they know the time, but mention it only now and then or when it fits (he asks, says goodnight, or it's very late), and otherwise follow what he's talking about. Likely fix: soften the time line in the prompt ("background only, don't keep bringing it up") and count bedtime/sleep as a recent topic not to repeat. — personas.md / pond-script.md
- **Tablet keyboard still takes half the screen** (v02, found 2026-11-25). The v02 fix works (header, cards and latest message stay on screen), but with the keyboard open only half the screen is left, so very little chat is visible. Suggested fix: while typing, fold the header and cards into a slim bar so more of the chat shows. — web-page.md

## Fixed
- v02 (2026-11-25): Shelly not remembering (chat history + memory logging + non-fact filter; tested on the Sprite) and tablet keyboard hiding the top message (app pinned to the visible viewport).

## Was open
- **Shelly doesn't remember facts** (v01, found 2026-11-24). Told "my favourite colour is green", she doesn't remember it later, not even in the same chat. Expected: one line in `pond/memory/turtle.md`. Note: `ask()` in `pond/pond.py` silently ignores any failure of the memory call, so the cause is hidden; check the memory file on the Sprite and log the error. — pond-script.md
  - Checked on the Sprite 2026-11-24 20:25: `turtle.md` does hold "Favourite colour is green." (written 20:09) and the memory call works when run by hand. Only 2 facts saved from ~16 messages; no errors in the service log, but memory-call errors and NONE answers are never logged, so we can't tell which messages failed. Still unclear why she didn't use the saved fact when asked. Next step: log the memory call's raw answer and any error, then retest "favourite colour" → ask again.
- **Tablet keyboard hides the top message** (v01, found 2026-11-24). When the on-screen keyboard opens, it pushes the top of the page off screen so the latest/top message can't be read. — web-page.md
