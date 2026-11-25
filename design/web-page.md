# Web page

Small Python web server on the Sprite, reached at the Sprite's own URL (wakes the Sprite on request).

## Agreed but not built
- `GET /` — the page: three animal cards (my son's drawings), chat area, "pond news" panel showing the gossip log.
- `POST /talk` — `{animal, text}` → pond script → `{animal, reply, drawing?}`.
- Replies shown with the animal's picture next to them.
- Works well on a tablet.
- Chat history (agreed 2026-11-24, v01 feedback): the page keeps the current chat so the animal can see the last 10 messages plus a summary of older ones (see pond-script.md). A reload starts a fresh chat.
- Smaller text on phones (agreed 2026-11-25, v01 feedback): on narrow phone screens the messages are too big; shrink text there while the tablet keeps its big text.
- Opening greeting comes from the animal (friendly, using its memory) instead of the fixed "Hello there!".

## Built
- v01: basic one-animal chat page at `GET /?key=…`; `POST /talk` `{animal, text}` → `{animal, reply}` with `X-Pond-Key` header. No key → 404.
- v01: private via secret key in the link (pond/secret_key.txt on the Sprite).

## Ideas (not agreed)
- Mockup to show my son before building.
