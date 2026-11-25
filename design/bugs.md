# Bugs

## Open
(none)

## Fixed
- v02 (2026-11-25): Shelly not remembering (chat history + memory logging + non-fact filter; tested on the Sprite) and tablet keyboard hiding the top message (app pinned to the visible viewport).

## Was open
- **Shelly doesn't remember facts** (v01, found 2026-11-24). Told "my favourite colour is green", she doesn't remember it later, not even in the same chat. Expected: one line in `pond/memory/turtle.md`. Note: `ask()` in `pond/pond.py` silently ignores any failure of the memory call, so the cause is hidden; check the memory file on the Sprite and log the error. — pond-script.md
  - Checked on the Sprite 2026-11-24 20:25: `turtle.md` does hold "Favourite colour is green." (written 20:09) and the memory call works when run by hand. Only 2 facts saved from ~16 messages; no errors in the service log, but memory-call errors and NONE answers are never logged, so we can't tell which messages failed. Still unclear why she didn't use the saved fact when asked. Next step: log the memory call's raw answer and any error, then retest "favourite colour" → ask again.
- **Tablet keyboard hides the top message** (v01, found 2026-11-24). When the on-screen keyboard opens, it pushes the top of the page off screen so the latest/top message can't be read. — web-page.md
